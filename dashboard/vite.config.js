import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import fs from 'fs'
import path from 'path'
import { WebSocketServer } from 'ws'

const rootDir = path.resolve(__dirname, '..')
const metricsDir = path.join(rootDir, 'storage', 'metrics')

function readJsonFile(fileName) {
  const filePath = path.join(metricsDir, fileName)

  if (!fs.existsSync(filePath)) {
    return null
  }

  return JSON.parse(fs.readFileSync(filePath, 'utf-8'))
}

function readJsonlFile(fileName) {
  const filePath = path.join(metricsDir, fileName)

  if (!fs.existsSync(filePath)) {
    return []
  }

  return fs
    .readFileSync(filePath, 'utf-8')
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line) => JSON.parse(line))
}

function readObservabilityData() {
  return {
    metrics: readJsonlFile('pipeline_metrics.jsonl'),
    status: readJsonFile('pipeline_status.json'),
    incidents: readJsonlFile('incident_log.jsonl'),
  }
}

function observabilityApi() {
  let wss = null
  const clients = new Set()
  let watcher = null
  let broadcastTimer = null

  function broadcast() {
    if (broadcastTimer) {
      clearTimeout(broadcastTimer)
    }

    broadcastTimer = setTimeout(() => {
      try {
        const message = JSON.stringify({
          type: 'observability_update',
          data: readObservabilityData(),
          timestamp: new Date().toISOString(),
        })

        for (const client of clients) {
          if (client.readyState === 1) {
            client.send(message)
          }
        }
      } catch (error) {
        console.error('[WebSocket] Broadcast error:', error.message)
      }
    }, 100)
  }

  return {
    name: 'icestream-observability-api',

    configureServer(server) {
      server.middlewares.use('/api/observability', (req, res) => {
        try {
          const data = readObservabilityData()

          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify(data))
        } catch (error) {
          res.statusCode = 500
          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify({
            error: error.message,
          }))
        }
      })

      server.httpServer?.on('upgrade', (request, socket, head) => {
        const url = new URL(
          request.url,
          `http://${request.headers.host || 'localhost'}`
        )

        if (url.pathname !== '/ws/observability') {
          return
        }

        if (!wss) {
          wss = new WebSocketServer({ noServer: true })

          wss.on('connection', (client) => {
            clients.add(client)

            console.log(
              `[WebSocket] Client connected. Total clients: ${clients.size}`
            )

            client.send(JSON.stringify({
              type: 'observability_update',
              data: readObservabilityData(),
              timestamp: new Date().toISOString(),
            }))

            client.on('close', () => {
              clients.delete(client)

              console.log(
                `[WebSocket] Client disconnected. Total clients: ${clients.size}`
              )
            })

            client.on('error', (error) => {
              console.error(
                '[WebSocket] Client error:',
                error.message
              )

              clients.delete(client)
            })
          })
        }

        wss.handleUpgrade(request, socket, head, (client) => {
          wss.emit('connection', client, request)
        })
      })

      if (fs.existsSync(metricsDir)) {
        watcher = fs.watch(
          metricsDir,
          { persistent: false },
          (_eventType, fileName) => {
            if (!fileName) {
              return
            }

            const watchedFiles = new Set([
              'pipeline_metrics.jsonl',
              'pipeline_status.json',
              'incident_log.jsonl',
            ])

            if (watchedFiles.has(fileName.toString())) {
              console.log(
                `[WebSocket] Observability file changed: ${fileName}`
              )

              broadcast()
            }
          }
        )
      }
    },

    closeBundle() {
      if (watcher) {
        watcher.close()
      }

      if (broadcastTimer) {
        clearTimeout(broadcastTimer)
      }

      if (wss) {
        wss.close()
      }
    },
  }
}

export default defineConfig({
  plugins: [
    react(),
    observabilityApi(),
  ],
})
