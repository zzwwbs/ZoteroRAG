# API Specification

## REST API Specification

```yaml
openapi: 3.0.0
info:
  title: ZoteroRAG Desk External API Interactions
  version: 1.0
  description: This specification outlines the external REST API interactions for the ZoteroRAG Desk application, primarily focusing on calls to OpenAI-compatible endpoints for text embeddings and AI analysis.
servers:
  - url: "{{user_configured_api_base_url}}"
    description: User-configured base URL for OpenAI-compatible API (e.g., OpenAI, Azure OpenAI, local LLM APIs)
paths:
  /v1/embeddings:
    post:
      summary: Generates vector embeddings for input text.
      description: Sends text input to the configured embedding model to obtain vector representations.
      operationId: createEmbedding
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - input
                - model
              properties:
                input:
                  type: array
                  items:
                    type: string
                  description: Input text to embed, encoded as a string or array of tokens.
                model:
                  type: string
                  description: The ID of the model to use for embeddings.
                encoding_format:
                  type: string
                  enum: [float, base64]
                  default: float
                  description: The format to return the embeddings in.
      responses:
        '200':
          description: Successful response with embedding vectors.
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      type: object
                      properties:
                        embedding:
                          type: array
                          items:
                            type: number
                        index:
                          type: number
                  model:
                    type: string
                  usage:
                    type: object
                    properties:
                      prompt_tokens:
                        type: number
                      total_tokens:
                        type: number
        '400':
          description: Bad Request - Invalid input or parameters.
        '401':
          description: Unauthorized - Invalid API key.
        '429':
          description: Too Many Requests - Rate limit exceeded.
  /v1/chat/completions:
    post:
      summary: Generates chat completions (AI analysis/synthesis).
      description: Sends a series of messages to the configured chat model to obtain a generated response.
      operationId: createChatCompletion
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - messages
                - model
              properties:
                messages:
                  type: array
                  items:
                    type: object
                    required:
                      - role
                      - content
                    properties:
                      role:
                        type: string
                        enum: [system, user, assistant]
                      content:
                        type: string
                model:
                  type: string
                  description: The ID of the model to use for chat completions.
                temperature:
                  type: number
                  format: float
                  default: 0.7
                  description: What sampling temperature to use.
                max_tokens:
                  type: number
                  description: The maximum number of tokens to generate.
      responses:
        '200':
          description: Successful response with chat completion.
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                  object:
                    type: string
                  created:
                    type: number
                  model:
                    type: string
                  choices:
                    type: array
                    items:
                      type: object
                      properties:
                        index:
                          type: number
                        message:
                          type: object
                          properties:
                            role:
                              type: string
                            content:
                              type: string
                        finish_reason:
                          type: string
                  usage:
                    type: object
                    properties:
                      prompt_tokens:
                        type: number
                      completion_tokens:
                        type: number
                      total_tokens:
                        type: number
        '400':
          description: Bad Request - Invalid input or parameters.
        '401':
          description: Unauthorized - Invalid API key.
        '429':
          description: Too Many Requests - Rate limit exceeded.
```
