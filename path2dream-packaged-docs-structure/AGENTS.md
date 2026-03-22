# Repo structure
This repo follow following documents structure:
- The repo has several packages
- Each package contains its own `docs` folder
- In `docs` folder there are following files:
  - USER_VISION.md
  - INTERFACE.md
  - _AI_CONTRIBUTION.md

## What each file means

### USER_VISION.md
This file contains all requirements for the module that user explicitly mentioned in the chat.
It might be any kind of requirements: functional, non-functional, implementation details.
In other words, it is a summary of user's vision of this package.
It should be concise, yet capturing all things important for user.
The file stores only things that user explicitly mentioned, not things that AI assistant assumed or recommended. But if assistant assumed something and user approved it - it also has to be documented here.

### INTERFACE.md
- Summary of the package "responsibility" - what does it do
  - The main idea is to keep package follow "single-responsibility" principle and do not do anything outside of it
- List of recommended to use public interfaces of the module, including all input args and output with typing, comments on how to use, limitations
  - The main idea is to keep interfaces minimalistic and clear, so it is very to start using the package, without need to dig deeper into implementation
  - The file documents only recommended way to use the package (happy path), without details on customization (which is out of the scope of this file)
  - Recommended structure:
    - Keep possibility to low-level configuration (by dependency inversion), but do not document it too much, as it is not recommended user's flow. If developer need customization, they will read the code, so we do not document it here.
    - Make a plug-and-play default interface, that provides best defaults, so any developer can start using the package though it, without figuring out what to provide for each arg. For this default builder, keep the list of args minimal. This "happy path" is well described in this file.
  - This file does not reveal implementation details
- Environment requirements: if the module needs some env vars, describe it here

### _AI_CONTRIBUTION.md
It is a detailed low-level documentation of all architectural decision. Everything new developer needs to know to immediately understand the current package state. All decision, potential problems, dev notes need to be documented here.

Also, this file contains QA policy of the package. Describe, what gates should pass after code changes.

## Docs policy

### Default policy
Docs should be short and minimalistic, prioritizing fast readability over being detailed and formal.
The main goal is to save time of the user who reads them. Make them as short as possible, while delivering the file purpose.

### AI policy
For files with `_AI_` prefix the policy is reverse: you need to be very detailed, preferring full explanation over brevity. Provide as many details as possible, so it is easier of other AI agents to fast start the work with the package.
