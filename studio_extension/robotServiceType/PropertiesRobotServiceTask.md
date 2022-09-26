---
# This is a comment, which might be helpful to explain the concept of help texts
title: Robot Service Task
---

# Robot Service Task

The `Robot Service Task` is a type of `External Service Task` that is used to delegate a unit of work to an external system, known as `Robot`.

### Agent

An `Agent` is a worker, which provides only `Robots`. `Agents` can be configured by executing the command 'Robot Agents: Configure Agents' from the command search.

### Topic

A `Topic` is used to identify a `Robot` and describes the type of work that needs to be completed.
`Agents` need to provide a interface for fetching all `Topics` they can handle.
This ensures that each `Robot Service Task` is delegated to an `Agent` that is able to process it.
Therefore the `Topic` may only by selected, while the selected `Agent` is running.
