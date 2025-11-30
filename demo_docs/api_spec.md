openapi: 3.0.0
info:
  title: User Service API
  version: 1.2.0
paths:
  /users:
    post:
      summary: Create a new user
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/User'
      responses:
        '201':
          description: User created successfully
        '401':
          description: Unauthorized - Missing or invalid token
components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
