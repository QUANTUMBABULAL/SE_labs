# Software Engineering Lab 03: Component Modelling & Architectural Pattern Selection

**Problem Statement #41: OpenAPI Mock Server Generator**

## Architecture: Layered (N-Tier)

| Layer | Components |
|-------|------------|
| Presentation | Developer Web UI / CLI, Mock HTTP Gateway |
| Application / Service | Spec Upload Service, Spec Parser & Validator, Endpoint Generator, Mock Data Generator, Request Router, Latency Simulator |
| Data | Specification Repository, Endpoint Registry |

**Why this architecture**
- **Separation of concerns:** parsing and validating specs, generating fake data and serving HTTP are independent and can be tested on their own.
- **Simple to build and deploy:** the tool ships as one package for a laptop or CI pipeline.
- **Security:** every uploaded spec passes one validation path before it reaches generation or storage. The public gateway only has read-only lookup access.
- **Performance:** endpoints are generated once at upload time, so the request path is an in-memory lookup plus non-blocking latency. This supports the NFR-001 target of 1,000 req/s with ±10 ms accuracy.

## Contents

| File | Description |
|------|-------------|
| `PES2UG24AM198_SELAB03.pdf` | Lab report: architecture choice, reasons, security and performance, components, diagram |
| `lab3_component_diagram.png` | UML component diagram |
| `lab3.drawio.svg` | Diagram in SVG format |
| `lab3_component_diagram.drawio` | Editable source (open in [diagrams.net](https://app.diagrams.net)) |

## Author

Chinmai A S · PES2UG24AM198 · PES University, Dept. of CSE
