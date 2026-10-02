# Grafana configuration

Run helpers from the intended checkout (Git's nearest repository/worktree root).
Outside Git, cwd is the root. Only `.agents/local/.env.agents` is discovered;
`--env-file PATH` overrides it. No parent checkout, application `.env`, or inherited
GRAFANA_* credential fallback is used. Values are parsed as dotenv data, without
shell evaluation or variable interpolation. Do not set credentials through shell
command arguments.

Copy [the example](../assets/env.agents.example) into the consumer's ignored local
path and fill it privately. Set a read-only Grafana user with access only to needed
datasources. Credentials still allow data access; instruction-level read-only
rules do not replace server permissions. Require HTTPS except a documented local
fixture/tunnel. Use a base URL without credentials, query or fragment.

| Variable | Meaning |
| --- | --- |
| GRAFANA_URL | Single instance base URL, including optional subpath. |
| GRAFANA_USERNAME, GRAFANA_PASSWORD | Grafana password login. |
| GRAFANA_BASIC_AUTH_USER, GRAFANA_BASIC_AUTH_PASSWORD | Optional ingress credentials; supply both or neither. |
| GRAFANA_INSTANCES | Optional comma-separated IDs; explicit --instance required for multiple IDs. |
| GRAFANA_<ID>_URL, GRAFANA_<ID>_BASIC_AUTH_PASSWORD | Per-instance URL and optional ingress password; ID uppercased with punctuation replaced by underscores. |

Multi-instance login username/password and ingress username are shared. Use
separate env files when environments have different login identities. A successful
health request does not prove login or datasource access. Responses/exports may
contain personal data even though configuration diagnostics hide credentials.
