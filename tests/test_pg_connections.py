"""Connection compatibility and live disposable PostgreSQL tests."""
import os
from pathlib import Path
import unittest
from urllib.parse import quote
import test_access as support
from test_access import postgres, POSTGRES, AccessError


class Configuration(unittest.TestCase):
    setUp = support.Contracts.setUp
    cli = support.Contracts.cli


class ConnectionConfiguration(Configuration):
    def test_url_and_pg_fields_precedence(self):
        config = postgres.connection_config({
            'DATABASE_URL': 'postgresql://url_user:p%40ss%26word@localhost/url_db?sslmode=require',
            'PGHOST': 'wrong', 'PGDATABASE': 'wrong', 'PGUSER': 'wrong',
            'PGPASSWORD': 'wrong', 'PGSSLMODE': 'disable',
        })
        self.assertEqual((config['host'], config['user'], config['password'], config['dbname']),
                         ('localhost', 'url_user', 'p@ss&word', 'url_db'))
        self.assertEqual(config['sslmode'], 'require')
        pg = postgres.connection_config({'PGHOST': 'localhost', 'PGPORT': '5433',
            'PGDATABASE': 'example', 'PGUSER': 'reader', 'PGPASSWORD': 'secret'})
        self.assertEqual(pg['port'], 5433)
        self.assertEqual(pg['sslmode'], 'prefer')
        system = postgres.connection_config({'DATABASE_URL': 'postgresql://u:p@localhost/db', 'PGSSLROOTCERT': 'system'})
        self.assertEqual(system['sslmode'], 'verify-full')

    def test_schema_and_relative_certificates(self):
        ca = self.local / 'ca.pem'; ca.write_text('fixture')
        env = {'DATABASE_URL': 'postgresql://u:p@localhost/db?schema=odd%20%22schema&pool_timeout=0&connection_limit=2&pgbouncer=true',
               'PGSSLROOTCERT': 'ca.pem'}
        config = postgres.connection_config(env, self.local)
        self.assertEqual(config['_schema'], 'odd "schema')
        self.assertEqual(config['sslrootcert'], str(ca.resolve()))
        self.assertNotIn('pool_timeout', config)
        env['DATABASE_URL'] += '&sslrootcert=missing.pem'
        with self.assertRaisesRegex(AccessError, 'sslrootcert'):
            postgres.connection_config(env, self.local)

    def test_invalid_configuration_has_no_secret(self):
        for suffix in ('?schema=', '?schema=%00', '?options=secret', '?host=secret',
                       '?connect_timeout=0', '?connect_timeout=61', '?schema=%GG',
                       '?connection_limit=0', '?pgbouncer=secret'):
            with self.subTest(suffix=suffix), self.assertRaises(AccessError) as ctx:
                postgres.connection_config({'DATABASE_URL': 'postgresql://u:secret@localhost/db'+suffix})
            self.assertNotIn('secret', str(ctx.exception))

    def test_case_expression_is_not_transaction_end(self):
        for sql in ("SELECT CASE WHEN true THEN 42 ELSE 0 END", "SELECT CASE WHEN true THEN CASE WHEN true THEN 1 END END", "SELECT 'END', $$END$$, \"END\"", "SELECT 1 /* END /* nested */ END */"):
            self.assertFalse(postgres.has_transaction_end(sql), sql)
        for sql in ("END", "-- CASE\nEND", "/* CASE /* nested */ */ END", "SELECT CASE WHEN true THEN 1 END; END"):
            self.assertTrue(postgres.has_transaction_end(sql), sql)

    def test_safe_diagnostics(self):
        for error, category in [
            (postgres.psycopg.OperationalError('certificate verify failed secret'), '[tls]'),
            (postgres.psycopg.OperationalError('could not translate host name secret'), '[dns]'),
            (postgres.psycopg.OperationalError('connection refused secret'), '[connection-refused]'),
            (postgres.psycopg.OperationalError('password authentication failed secret'), '[authentication]'),
            (postgres.psycopg.errors.UndefinedColumn('secret'), '[schema]'),
            (postgres.psycopg.errors.InsufficientPrivilege('secret'), '[permissions]'),
        ]:
            result = str(postgres.database_error(error))
            self.assertIn(category, result)
            self.assertNotIn('secret', result)


@unittest.skipUnless(os.environ.get('SKILLS_TEST_TLS_DATABASE_URL'), 'requires disposable TLS fixture')
class LiveConnections(Configuration):
    def config(self, suffix='', **env):
        return postgres.connection_config({'DATABASE_URL': os.environ['SKILLS_TEST_TLS_DATABASE_URL'] + suffix, **env})

    def test_tls_modes_and_ca(self):
        for mode, active in [('disable', False), ('prefer', True), ('require', True),
                             ('verify-ca', True), ('verify-full', True)]:
            cfg = self.config('?sslmode='+mode, PGSSLROOTCERT=os.environ['SKILLS_TEST_CA'])
            result = postgres.read_query(cfg, 'SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()')
            self.assertEqual(result['rows'][0]['ssl'], active)
        cfg = self.config('?sslmode=verify-full', PGSSLROOTCERT=os.environ['SKILLS_TEST_WRONG_CA'])
        with self.assertRaisesRegex(AccessError, r'\[tls\]'):
            postgres.read_query(cfg, 'SELECT 1')
        cfg = self.config('?sslmode=verify-full', PGSSLROOTCERT=os.environ['SKILLS_TEST_CA'])
        cfg['host'] = '127.0.0.1'  # fixture certificate deliberately only names localhost
        with self.assertRaisesRegex(AccessError, r'\[tls\]'):
            postgres.read_query(cfg, 'SELECT 1')

    def test_no_tls_server_default_and_strict_failure(self):
        url = os.environ['SKILLS_TEST_DATABASE_URL'].split('?')[0]
        result = postgres.read_query(postgres.connection_config({'DATABASE_URL': url}),
                                     'SELECT ssl FROM pg_stat_ssl WHERE pid = pg_backend_pid()')
        self.assertFalse(result['rows'][0]['ssl'])
        with self.assertRaisesRegex(AccessError, r'\[tls\]'):
            postgres.read_query(postgres.connection_config({'DATABASE_URL': url+'?sslmode=require'}), 'SELECT 1')

    def test_schema_selection_and_read_only(self):
        schema = 'fixture "quoted; schema'
        # Provision test-owned objects through a separate fixture connection.
        with postgres.psycopg.connect(os.environ['SKILLS_TEST_TLS_DATABASE_URL'], autocommit=True) as conn:
            conn.execute(postgres.psycopg.sql.SQL('CREATE SCHEMA {}').format(postgres.psycopg.sql.Identifier(schema)))
            try:
                conn.execute(postgres.psycopg.sql.SQL('CREATE TABLE {}.sample (value integer)').format(postgres.psycopg.sql.Identifier(schema)))
                conn.execute(postgres.psycopg.sql.SQL('INSERT INTO {}.sample VALUES (42)').format(postgres.psycopg.sql.Identifier(schema)))
                cfg = self.config('?schema='+quote(schema, safe='')+'&pgbouncer=true')
                self.assertEqual(postgres.read_query(cfg, 'SELECT CASE WHEN value = 42 THEN value ELSE 0 END AS value FROM sample')['rows'], [{'value': 42}])
                self.assertEqual(postgres.read_query(cfg, "SELECT current_schema() AS schema, current_setting('transaction_read_only') AS ro")['rows'], [{'schema': schema, 'ro': 'on'}])
                with self.assertRaisesRegex(AccessError, r'\[read-only\]'):
                    postgres.read_query(cfg, 'INSERT INTO sample VALUES (1)')
                with self.assertRaisesRegex(AccessError, 'SQLSTATE=42601'):
                    postgres.read_query(cfg, 'SELECT 1; SELECT 2')
            finally:
                conn.execute(postgres.psycopg.sql.SQL('DROP SCHEMA {} CASCADE').format(postgres.psycopg.sql.Identifier(schema)))
        with self.assertRaisesRegex(AccessError, r'\[schema\]'):
            postgres.read_query(self.config('?schema=missing_fixture_schema'), 'SELECT 1')

    def test_auth_sql_and_cli(self):
        cfg = self.config(); cfg['password'] = 'wrong-fixture-password'
        with self.assertRaisesRegex(AccessError, r'\[authentication\]') as ctx:
            postgres.read_query(cfg, 'SELECT 1')
        self.assertNotIn('wrong-fixture-password', str(ctx.exception))
        with self.assertRaisesRegex(AccessError, r'\[schema\].*42703'):
            postgres.read_query(self.config(), 'SELECT nonexistent_fixture_column')
        self.envfile.write_text('DATABASE_URL='+os.environ['SKILLS_TEST_TLS_DATABASE_URL']+'?schema=public\n')
        result = self.cli(POSTGRES, 'check', '--env-file', str(self.envfile))
        self.assertEqual(result.returncode, 0, result.stderr)
        import json
        row = json.loads(result.stdout)['rows'][0]
        self.assertEqual(row['current_schema'], 'public')
        self.assertEqual(row['transaction_read_only'], 'on')
        self.assertTrue(row['tls_active'])

    def test_pg_fields_and_relative_ca_through_cli(self):
        from urllib.parse import urlsplit
        import shutil
        url = urlsplit(os.environ['SKILLS_TEST_TLS_DATABASE_URL'])
        shutil.copyfile(os.environ['SKILLS_TEST_CA'], self.local/'ca.pem')
        self.envfile.write_text(
            f'PGHOST={url.hostname}\nPGPORT={url.port}\nPGDATABASE={url.path[1:]}\n'
            f'PGUSER={url.username}\nPGPASSWORD={url.password}\n'
            'PGSSLMODE=verify-full\nPGSSLROOTCERT=ca.pem\n')
        result = self.cli(POSTGRES, 'check', '--env-file', str(self.envfile))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('fixture-password', result.stdout+result.stderr)

    def test_database_permissions_and_timeout(self):
        cfg = self.config(); cfg['dbname'] = 'missing_fixture_database'
        with self.assertRaisesRegex(AccessError, r'\[database\]'):
            postgres.read_query(cfg, 'SELECT 1')
        cfg = self.config()
        cfg['options'] += ' -c statement_timeout=50'
        with self.assertRaisesRegex(AccessError, r'\[timeout\]'):
            postgres.read_query(cfg, 'SELECT pg_sleep(2)')
        with postgres.psycopg.connect(os.environ['SKILLS_TEST_TLS_DATABASE_URL'], autocommit=True) as conn:
            conn.execute("CREATE ROLE fixture_reader LOGIN PASSWORD 'fixture-reader-password'")
            conn.execute('CREATE SCHEMA fixture_private')
            try:
                cfg = self.config('?schema=fixture_private')
                cfg.update(user='fixture_reader', password='fixture-reader-password')
                with self.assertRaisesRegex(AccessError, r'\[permissions\]'):
                    postgres.read_query(cfg, 'SELECT 1')
            finally:
                conn.execute('DROP SCHEMA fixture_private')
                conn.execute('DROP ROLE fixture_reader')
