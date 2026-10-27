# Kestrel Learning — Analytics Engineer: технічна співбесіда

Kestrel Learning — вигадана компанія, яка продає підписки на онлайн-репетиторство. Усі дані, назви й структури в цих репозиторіях синтетичні.

## Репозиторії

| Репозиторій | Що там |
|---|---|
| [interview-deploy-projects](https://github.com/vdbrsk/interview-deploy-projects) | Цей репозиторій: self-service проєкти (репорти, дашборди, алерти, автоматизації) |
| [interview-data-dbt](https://github.com/vdbrsk/interview-data-dbt) | dbt-проєкт: staging, intermediate, marts |
| [interview-data-cube](https://github.com/vdbrsk/interview-data-cube) | Semantic layer (Cube) над marts |
| [interview-mcp-server](https://github.com/vdbrsk/interview-mcp-server) | MCP-сервер, через який AI-агенти працюють з даними та репортами |

Код у репозиторіях призначений для читання й аналізу; запускати нічого не потрібно, реальних сервісів і доступів немає.

## Постановка

Ми маємо self-service data platform, де бізнес-користувачі та AI-агенти можуть створювати репорти, аналітичні інструменти й автоматизації.

У міру масштабування різні проєкти почали по-різному обчислювати однакові бізнес-метрики.

Ми хочемо забезпечити використання canonical metrics із semantic layer, зберігаючи гнучкість платформи.

Досліди систему, визнач основні проблеми, запропонуй архітектурне рішення та, за можливості, реалізуй його мінімальну частину.

Можна використовувати будь-які AI-інструменти. Повне рішення за час співбесіди не очікується.
