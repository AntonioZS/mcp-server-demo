## HTTP normal vs Streamable HTTP

### HTTP normal (request/response clásico)

```
Cliente          Servidor
  |                  |
  |--- POST /tool -->|
  |                  |  (servidor procesa)
  |<-- 200 {result}--|
  |                  |
```

- Una petición → una respuesta → conexión cerrada.
- El servidor no puede enviar nada hasta que el cliente pregunta.
- Si la operación tarda 10 segundos, el cliente espera bloqueado sin saber qué pasa.

---

### Streamable HTTP (lo que usa este repo)

```
Cliente               Servidor
  |                       |
  |--- POST /mcp/ ------->|   (initialize)
  |<-- 200 session-id ----|
  |                       |
  |--- POST /mcp/ ------->|   (call_tool)
  |<-- SSE stream --------|   event: processing file 1...
  |<-- SSE stream --------|   event: processing file 2...
  |<-- SSE stream --------|   event: done → {result}
  |                       |
  |--- DELETE /mcp/ ----->|   (terminate session)
```

- La **conexión se mantiene abierta** durante la operación.
- El servidor puede **enviar eventos incrementales** mientras trabaja (progress notifications).
- Se usa `text/event-stream` (SSE) para el canal de vuelta.
- Lo ves en acción en [`process_project_files`](mcp_demo/tools/catalog.py ) con los `await ctx.info(...)`.

En este repo puedes ver el mecanismo en [`mcp.client.streamable_http.streamablehttp_client`]client.py ) y en el servidor en streamable_http.py.

---

### Tabla comparativa

| | HTTP normal | Streamable HTTP |
|---|---|---|
| Conexión | Se cierra tras cada respuesta | Se mantiene abierta durante la operación |
| Progreso | No | Sí, via SSE events |
| Sesión | Stateless por defecto | Stateful con `mcp-session-id` |
| Cancelación | No | Sí, vía DELETE |
| Resumibilidad | No | Sí, vía `last-event-id` |
| Latencia percibida | Alta en ops largas | Baja, feedback inmediato |
| Infraestructura | Cualquier proxy/balanceador | Requiere soporte de streaming (timeouts largos, no buffering) |

---

### ¿Cuál es el habitual en producción?

**Depende del caso de uso:**

- **HTTP normal** → APIs REST clásicas, CRUD, operaciones cortas. Es el 95% del tráfico web.
- **Streamable HTTP / SSE** → operaciones largas, AI inference, pipelines, agentes. Está creciendo mucho con LLMs.
- **WebSockets** → sistemas de tiempo real bidireccional (chat, trading, juegos).

En el **contexto MCP específicamente**:
- **Streamable HTTP es el transporte recomendado para producción** según la spec oficial de MCP.
- SSE puro (el otro transporte de MCP) está siendo deprecado en favor de streamable HTTP.
- stdio solo se usa para procesos locales (CLI tools, extensiones de editor).

La razón práctica: streamable HTTP funciona bien detrás de **cualquier reverse proxy** (nginx, API Gateway, Azure APIM) porque usa HTTP/HTTPS estándar. Solo hay que ajustar los **timeouts** para no cortar conexiones largas.