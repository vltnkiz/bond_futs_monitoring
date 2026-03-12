# DDD Rules

## Aggregates

### 1. Aggregates protect transactional boundaries

- Only the aggregate itself can modify its internal state (encapsulation / "Tell, don't ask").
- Business invariants must be enforced inside the aggregate or its value objects.
- An aggregate is a cluster of domain objects treated as a single unit.
- An aggregate defines both a consistency boundary and a transactional boundary.
- Each command is executed within one SQL transaction, which is rolled back if an exception occurs.

---

### 2. Business rules belong in the domain model

- Business logic must not be implemented in the service or use-case layer.
- All business logic belongs inside the domain model.

**Use-case layer responsibilities:**
- The use case layer should remain thin.
- It orchestrates interactions between the domain model and the application layer (e.g., web layer).
- The use case acts as the primary port in a hexagonal architecture.
- It is the single entry point to the domain model.

**Testing strategy:**
- Unit tests should target use cases, not the domain model directly.
- The domain model is tested indirectly through use-case tests.

---

### 3. Keep aggregates small

- Aggregates must be small enough to be loaded into memory and processed in one transaction.
- They should keep the domain model simple and maintainable.
- Aggregates should remain highly cohesive, focusing on a clear responsibility.

---

### 4. Reference other aggregates by ID only

- Aggregates must not hold direct object references to other aggregates.
- Instead, they reference other aggregates by their ID.

**Infrastructure guidelines:**
- Use the Repository pattern.
- There should be one repository per aggregate.
- An ORM can be used to load aggregates.
- The repository is responsible for loading and saving aggregates.

**Database rules:**
- Do not use foreign keys between aggregates.
- Foreign keys are allowed between an aggregate and:
  - its value objects
  - its internal entities (non-aggregate entities)

---

### 5. Modify only one aggregate per transaction

- A single transaction should modify only one aggregate.
- Always consider concurrency issues.

**Concurrency strategies:**
- Use optimistic locking / versioning to prevent conflicts.
- Use eventual consistency to update other aggregates (via domain events).

**Exception:**
- It is acceptable to create multiple aggregates in one transaction, but never update more than one aggregate in the same transaction.

---

### 6. Aggregate creation

- Aggregates should not be instantiated directly.
- They are normally loaded from the database.
- When creation is required, use aggregate factories.

**Benefits:**
- Captures domain language in code.
- Encourages strong encapsulation and object-oriented design principles.

---

## Value Objects

### Definition

A Value Object is an object that is completely defined by its attributes.

**Properties:**
- Immutable (cannot be modified after creation).
- No identity.
- No lifecycle.
- No internal state changes.
- No side effects or domain events.