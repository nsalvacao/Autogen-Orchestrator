#!/usr/bin/env python
"""
REST API Adapter Example

This example demonstrates how to use the REST API adapter to integrate
with external APIs. The adapter supports multiple authentication methods,
HTTP methods, and provides async request handling.

Features demonstrated:
- Basic HTTP requests (GET, POST, PUT, DELETE)
- Different authentication types (Bearer, API Key)
- JSON and form data requests
- Error handling
- Custom headers

Requirements:
- pip install aiohttp
"""

import asyncio

from orchestrator.adapters.api_adapter import APIAdapter, AuthType, HTTPMethod
from orchestrator.contracts.adapter_contract import AdapterConfig, AdapterType


async def example_public_api():
    """Example using a public API (JSONPlaceholder)."""
    print("=" * 70)
    print("Example 1: Public API - JSONPlaceholder")
    print("=" * 70)
    
    # Create adapter for public API (no auth required)
    adapter = APIAdapter(
        base_url="https://jsonplaceholder.typicode.com",
        auth_type=AuthType.NONE,
        timeout=10,
    )
    
    # Connect to the API
    result = await adapter.connect()
    print(f"✓ Connected: {result.success}")
    print()
    
    # GET request - Fetch a post
    print("GET /posts/1")
    result = await adapter.get("/posts/1")
    if result.success:
        post = result.data["response"]
        print(f"  Title: {post['title']}")
        print(f"  Body: {post['body'][:50]}...")
    print()
    
    # GET request with query parameters
    print("GET /posts?userId=1")
    result = await adapter.get("/posts", params={"userId": 1})
    if result.success:
        posts = result.data["response"]
        print(f"  Found {len(posts)} posts for user 1")
    print()
    
    # POST request - Create a new post
    print("POST /posts")
    new_post = {
        "title": "Test Post from Orchestrator",
        "body": "This is a test post created via the API adapter",
        "userId": 1,
    }
    result = await adapter.post("/posts", json=new_post)
    if result.success:
        created = result.data["response"]
        print(f"  Created post with ID: {created['id']}")
    print()
    
    # PUT request - Update a post
    print("PUT /posts/1")
    updated_post = {
        "id": 1,
        "title": "Updated Title",
        "body": "Updated body content",
        "userId": 1,
    }
    result = await adapter.put("/posts/1", json=updated_post)
    if result.success:
        print(f"  Post updated successfully")
    print()
    
    # DELETE request
    print("DELETE /posts/1")
    result = await adapter.delete("/posts/1")
    if result.success:
        print(f"  Post deleted successfully")
    print()
    
    # Cleanup
    await adapter.disconnect()
    print("✓ Disconnected")
    print()


async def example_authenticated_api():
    """Example using an authenticated API pattern."""
    print("=" * 70)
    print("Example 2: Authenticated API with Bearer Token")
    print("=" * 70)
    
    # Create adapter with Bearer token authentication
    adapter = APIAdapter(
        base_url="https://api.example.com",
        auth_type=AuthType.BEARER,
        auth_token="your_api_token_here",
        timeout=30,
        headers={"Accept": "application/json"},
    )
    
    print("Configuration:")
    print(f"  Base URL: https://api.example.com")
    print(f"  Auth Type: Bearer Token")
    print(f"  Timeout: 30s")
    print()
    
    # Connect (this would fail without a real API, so we'll skip actual connection)
    print("Note: This example shows the configuration pattern.")
    print("In production, you would:")
    print("  1. await adapter.connect()")
    print("  2. await adapter.get('/api/resource')")
    print("  3. await adapter.disconnect()")
    print()


async def example_api_key_auth():
    """Example using API key authentication."""
    print("=" * 70)
    print("Example 3: API Key Authentication Pattern")
    print("=" * 70)
    
    # Create adapter with API Key authentication
    adapter = APIAdapter(
        base_url="https://api.service.com",
        auth_type=AuthType.API_KEY,
        auth_token="your_api_key_here",
        timeout=20,
    )
    
    print("Configuration:")
    print(f"  Base URL: https://api.service.com")
    print(f"  Auth Type: API Key (X-API-Key header)")
    print(f"  Timeout: 20s")
    print()
    
    print("Usage pattern:")
    print("  # GET with API key")
    print("  result = await adapter.get('/v1/data')")
    print()
    print("  # POST with API key and JSON body")
    print("  result = await adapter.post('/v1/data', json={'key': 'value'})")
    print()


async def example_custom_request():
    """Example using custom request method."""
    print("=" * 70)
    print("Example 4: Custom HTTP Requests")
    print("=" * 70)
    
    adapter = APIAdapter(
        base_url="https://jsonplaceholder.typicode.com",
        auth_type=AuthType.NONE,
    )
    
    await adapter.connect()
    
    # Using the generic request method
    print("Custom request with execute():")
    result = await adapter.execute(
        "/posts",
        method="GET",
        params={"_limit": 3},
    )
    
    if result.success:
        posts = result.data["response"]
        print(f"  Retrieved {len(posts)} posts")
        for post in posts:
            print(f"    - {post['title'][:40]}...")
    print()
    
    # Using the request() helper
    print("Using request() helper:")
    result = await adapter.request(
        HTTPMethod.GET,
        "/users/1",
    )
    
    if result.success:
        user = result.data["response"]
        print(f"  User: {user['name']}")
        print(f"  Email: {user['email']}")
    print()
    
    await adapter.disconnect()


async def example_error_handling():
    """Example demonstrating error handling."""
    print("=" * 70)
    print("Example 5: Error Handling")
    print("=" * 70)
    
    adapter = APIAdapter(
        base_url="https://jsonplaceholder.typicode.com",
        auth_type=AuthType.NONE,
    )
    
    await adapter.connect()
    
    # Request to non-existent endpoint
    print("Requesting non-existent resource:")
    result = await adapter.get("/posts/99999")
    print(f"  Success: {result.success}")
    if not result.success:
        print(f"  Error: {result.error_message}")
    print()
    
    # Invalid HTTP method would be caught by type system
    # But here's how errors are handled in general
    print("Error handling pattern:")
    print("  result = await adapter.get('/endpoint')")
    print("  if result.success:")
    print("      data = result.data['response']")
    print("  else:")
    print("      print(f'Error: {result.error_message}')")
    print()
    
    await adapter.disconnect()


async def main():
    """Run all examples."""
    print("\n")
    print("*" * 70)
    print("REST API Adapter - Comprehensive Examples")
    print("*" * 70)
    print()
    
    # Run examples
    await example_public_api()
    await example_authenticated_api()
    await example_api_key_auth()
    await example_custom_request()
    await example_error_handling()
    
    print("=" * 70)
    print("All examples completed!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("  - Install aiohttp: pip install aiohttp")
    print("  - Configure your API endpoint and authentication")
    print("  - Use adapter.get(), post(), put(), delete() for requests")
    print("  - Handle errors using result.success and result.error_message")
    print()


if __name__ == "__main__":
    asyncio.run(main())
