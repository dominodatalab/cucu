# Cucu Run Database Requirements Spec

## Overview

Cucu needs to create and maintain a structured database to store all relevant test execution data from `cucu run` commands. This database will provide a comprehensive, queryable record of test results to enable better analysis, reporting, and debugging. The database will serve as a centralized repository for historical test data that can be used for trend analysis, test effectiveness reporting, and failure pattern detection.

## Prerequisites

This specification depends on the implementation of the enhanced section steps functionality described in the [Section Steps Implementation Specification](/Users/cedric.young/code/cucu/specs/section_steps_specs.md), which provides the hierarchical structure used by the database schema.

## Core Requirements

- **CLI Configuration**:
  - Add `--database/--no-database` flag to enable/disable database functionality (disabled by default)

- **Implementation Approach**:
  - Keep existing output artifacts (PNG files, directory structures, JSON, logs, etc.)
  - Create a single DuckDB database file at the start of a test run (if it doesn't exist)
  - The database is shared between all workers in a multi-worker run
  - Update the database in real-time at defined points in the test execution lifecycle
  - Ensure proper transaction management to prevent race conditions or deadlocks
  - Maintain database validity even if the cucu process or a worker is killed unexpectedly
  - Store file metadata in the database instead of the actual file contents
  - Register database operations in appropriate lifecycle hooks (before/after scenario, feature, etc.)
  - Use a connection pool mechanism to handle parallel worker access efficiently
  - Implement timeout mechanisms for database operations to prevent hanging

- **Performance Considerations**:
  - Minimize overhead of database operations during test execution
  - Implement database operations asynchronously where possible
  - Add periodic compaction/cleanup mechanism for long-term database health
  - Monitor and optimize query performance for large test suites
  - Batch database operations where appropriate to reduce transaction overhead
  - Implement indexes on frequently queried columns for performance
  - Consider implementing a worker-local cache for repeated queries
  - Add monitoring and logging of database operation performance

## Database Schema

The database schema is designed to follow the natural hierarchy of BDD testing, with tables linked through foreign keys to create a complete representation of test execution.

### Tables Structure

All tables have the following conventions:
- Primary key column named `{tablename}_id`
- Timestamps for creation and last update
- Status fields where appropriate (passed, failed, skipped, etc.)
- Descriptive fields for key metadata
- Foreign keys to establish relationships between tables
- Unique constraints where appropriate to prevent duplicate entries

### Tables Definition

1. **CucuRun**: Master record for each test execution
   - One record per `cucu run` command, even with multiple workers
   - Contains all command-line arguments, environment variables, and system information
   - Serves as the parent record for all other tables

2. **Feature**: Maps to a feature file
   - One record per feature file included in the run
   - Contains feature metadata (name, description, filename, tags)
   - Features don't execute directly, but contain scenarios that do

3. **Scenario**: Maps to a scenario within a feature file
   - Contains scenario metadata (name, description, tags, filename and linenumber)
   - Inherits tags from parent feature
   - Records execution statistics (duration, status, etc.)
   - Records cleanup activity

4. **StepDef**: Maps to either a step in a feature file or to a step used in run_steps
   - Contains step definition (name, kind (Given/When/Then/And/Section)
   - Metadata (filename and line number)
   - Header level (normally 0)
   - Step order number (starts from 1)
   - Records hierarchy information (parent step def, step level)
   1. **Section**:
      - Sets the header level 1-4 (using markdown headers #, ##, ###, ####)
   2. **SubStep**: Steps that have a parent step
      - Has a parent step (could be another step or a section step)

5. **StepRun**: Records each execution attempt of a step
   - Steps can be retried, so each attempt is a separate record
   - try attempt number (starting at 1 per StepDef)
   - Contains metadata (status, start, end, duration)
   - Has cucu debug log
   - Browser metadata for browser steps (browser log, broswer url, title, tab number, total tabs)
   - Links to associated screenshots and other artifacts in the artifacts table

6.  **Artifact**: Records file-based outputs
   - Stores metadata about generated files
   - Contains file data (name, path, stats)
   - For screenshots 
   - Links to associated test elements (steps, scenarios, etc.)
   - Artifact order number (starts at 1, order per StepRun)
   - Supports classification and categorization of different artifact types
