import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import fs from 'fs'
import path from 'path'

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

function observabilityApi() {
  return {
    name: 'icestream-observability-api',

    configureServer(server) {
      server.middlewares.use('/api/observability', (req, res) => {
        try {
          const data = {
            metrics: readJsonlFile('pipeline_metrics.jsonl'),
            status: readJsonFile('pipeline_status.json'),
            incidents: readJsonlFile('incident_log.jsonl'),
          }

          res.setHeader('Content-Type', 'application/json')
          res.end(JSON.stringify(data))
        } catch (error) {
          res.statusCode = 500
          res.setHeader('Content-Type', 'application/json')
          res.end(
            JSON.stringify({
              error: error.message,
            }),
          )
        }
      })
    },
  }
}

export default defineConfig({
  plugins: [
    react(),
    observabilityApi(),
  ],
})