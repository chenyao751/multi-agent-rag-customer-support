"""Aviation MCP Client

Encapsulates JSON-RPC 2.0 calls to the Aviation MCP service.
"""

import requests
import json
from typing import Dict, Any, Optional
from customer_support_chat.app.core.logger import logger
from customer_support_chat.app.core.settings import get_settings

settings = get_settings()


class AviationMCPClient:
    """Client for Aviation MCP service using JSON-RPC 2.0 protocol."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key or settings.AVIATION_MCP_API_KEY
        self.base_url = base_url or settings.AVIATION_MCP_BASE_URL
        self.request_id = 0
        self.timeout = 30  # 30 seconds as per documentation

        if not self.api_key:
            logger.warning("Aviation MCP API Key not configured")

    def _make_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make a JSON-RPC 2.0 request to the MCP service.

        Args:
            method: The JSON-RPC method name (e.g., "tools/list", "tools/call")
            params: Optional parameters for the method

        Returns:
            The result from the JSON-RPC response

        Raises:
            Exception: If the request fails or returns an error
        """
        self.request_id += 1

        payload = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method
        }

        if params:
            payload["params"] = params

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",  # Support both JSON and SSE
            "X-API-Key": self.api_key
        }

        try:
            logger.debug(f"Aviation MCP request: {method} with params: {params}")

            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=self.timeout
            )

            response.raise_for_status()
            result = response.json()

            logger.debug(f"Aviation MCP response: {result}")

            # Check for JSON-RPC error
            if "error" in result:
                error = result["error"]
                error_msg = f"MCP Error {error.get('code', 'unknown')}: {error.get('message', 'Unknown error')}"
                logger.error(error_msg)
                raise Exception(error_msg)

            return result.get("result", {})

        except requests.exceptions.Timeout:
            logger.error(f"Aviation MCP request timed out after {self.timeout}s")
            raise Exception(f"Aviation MCP request timed out after {self.timeout} seconds")

        except requests.exceptions.RequestException as e:
            logger.error(f"Aviation MCP request failed: {e}")
            raise Exception(f"Failed to connect to Aviation MCP service: {str(e)}")

        except Exception as e:
            logger.error(f"Aviation MCP error: {e}")
            raise

    def list_tools(self) -> Dict[str, Any]:
        """List all available tools from the MCP service.

        Returns:
            Dictionary containing available tools
        """
        return self._make_request("tools/list")

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a specific tool with given arguments.

        Args:
            tool_name: Name of the tool to call
            arguments: Dictionary of arguments for the tool

        Returns:
            The result from the tool execution
        """
        params = {
            "name": tool_name,
            "arguments": arguments
        }

        result = self._make_request("tools/call", params)

        # MCP tools/call returns a content array
        # Extract the actual content
        if isinstance(result, dict) and "content" in result:
            content = result["content"]
            if isinstance(content, list) and len(content) > 0:
                # Return the text content
                return content[0].get("text", content[0])
            return content

        return result


# Singleton instance
_mcp_client_instance = None


def get_mcp_client() -> AviationMCPClient:
    """Get the singleton MCP client instance."""
    global _mcp_client_instance
    if _mcp_client_instance is None:
        _mcp_client_instance = AviationMCPClient()
    return _mcp_client_instance
