# Core development principles:
- We write production software. Always prefer proper solutions over quick hacks. No compromises. No workarounds.
- Fail fast on unexpected situations
  - Zero fallbacks tolerance - fail fast, no fallbacks.
  - If you think that fallback unavoidable, get approval from user, do not introduce silent fallbacks
- Zero legacy tolerance 
  - make full proper refactorings
  - if you think that better to keep something "for backwards compatibility" - ask user's approval for it. Do not create legacy code silently.
- No errors hiding
  - If something does not work because of the problem in 3rd party library - do not work around it. Stop and report to user.
  - Properly fix linter warnings, do not hide them. If needed - do proper refactoring. Do not be lazy. Choose proper solutions over easy.

# Concurrent modifications
If you notice that some files are unexpectedly modified (not by you) - do not revert these changes,
probably the user is working on the same file. If it is blocking you - stop and contact the user to sync. Or if these changes are not breaking for you - proceed. But never revert unexpected changes!