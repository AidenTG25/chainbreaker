import { useEffect, useRef, useCallback } from 'react';

type MessageHandler = (data: unknown) => void;

export function useWebSocket(url: string, onMessage: MessageHandler) {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    try {
      wsRef.current = new WebSocket(url);
      wsRef.current.onopen = () => console.log('WS connected');
      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch {
          onMessage(event.data);
        }
      };
      wsRef.current.onclose = () => {
        reconnectTimeoutRef.current = setTimeout(connect, 5000);
      };
      wsRef.current.onerror = () => {
        wsRef.current?.close();
      };
    } catch {
      reconnectTimeoutRef.current = setTimeout(connect, 5000);
    }
  }, [url, onMessage]);

  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current);
      wsRef.current?.close();
    };
  }, []);

  return { connect };
}
