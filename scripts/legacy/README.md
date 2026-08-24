# Legacy maintenance utilities

This directory contains one-off repository migration helpers retained for historical reference.
They are not part of the application runtime or test suite and should not be executed against the
current source tree without review.

- `add_registry.py` was used during early development to inject a registry implementation into
  `backend/app/ml/model_loader.py`. The registry is already present in the current codebase.
