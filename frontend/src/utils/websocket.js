/**
 * connectWebSocket(searchId, onMessage, onError)
 * Auto-reconnects up to MAX_RETRIES times with exponential back-off.
 * Returns a disconnect() function.
 */
const MAX_RETRIES = 3
const BASE_DELAY  = 1500 // ms

export function connectWebSocket(searchId, onMessage, onError) {
  let ws      = null
  let retries = 0
  let stopped = false

  function connect() {
    if (stopped) return

    const url = `ws://${window.location.host}/ws/search/${searchId}/`
    ws = new WebSocket(url)

    ws.onopen = () => {
      retries = 0 // reset on successful connection
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch {
        // ignore malformed frames
      }
    }

    ws.onerror = () => {
      // onerror fires before onclose — handled in onclose
    }

    ws.onclose = () => {
      if (stopped) return
      if (retries < MAX_RETRIES) {
        const delay = BASE_DELAY * Math.pow(2, retries)
        retries++
        setTimeout(connect, delay)
      } else {
        onError && onError(new Error(`WebSocket failed after ${MAX_RETRIES} attempts`))
      }
    }
  }

  connect()

  return function disconnect() {
    stopped = true
    if (ws) {
      ws.onclose = null // prevent retry logic on intentional close
      ws.close()
    }
  }
}
