# <div align="center"> `function-calling-experiments` </div>

> This repository contains my experiments to discern Gemma 3's function
> calling capabilities.

## Defining the Capabilities

The following are capabilities that if present, open up a lot of possibilities with function calling in Gemma.

#### Choosing and Calling Functions

1. Choosing the right function and right time to call it.
2. Calling the right function with the right parameters.
3. Asking the user for missing details required by the function specification.
4. Support calling a large number of functions (> 20 maybe?).

#### Parallel and Composite Function Calling

5. Making independent function calls in parallel.
6. Receiving outputs from the function calls asynchronously and/or out of order.
7. Planning and using the results of one function to call another, i.e. composite function calling.

#### Explainability

8. Explaining the reasoning during the entire process of making a function call.

## Current Experiments

The `cumulative` experiment combines several ideas I had, and crosses
off points 1, 2, 3, 5, 6, and 8 (to some extent). This involves:

- introducing the concept of threads to make sure the model focuses only on relevant context.
- giving the model definitive courses of action that it can choose from.
- requesting the model to decode intent from the user's messages, instead of taking them literally.
- asking the model to think of different courses of action, and justify which one it should take.
- making use of code blocks (somewhat similar to other llms' usage of xml tags) to intersperse its natural language output with structured data.
- defining possible responses and errors from function calls, enabling the model to plan what it can do with the output.
- specifying that functions can be called parallely, but with the risk of asynchronous output.

The system prompt for the experiment is in [`experiments/cumulative/prompts/00-system-prompt.user`](experiments/cumulative/prompts/00-system-prompt.user),
while the function definitions are in [`experiments/cumulative/prompts/01-functions.user`](experiments/cumulative/prompts/01-functions.user).

## Running and Creating Experiments

Please install `uv` if you don't have `mise` or `uv` installed already.

You can bring up the runner with the following command:

```fish
uv run main.py
```

Enter the name of an experiment from the `experiments/` directory, and
it will start a chat with Gemma 3 with the prompts and functions defined
by the experiment:

```
experiments/
└── <name>/
    ├── outputs/
    │   └── <timestamp>.json
    ├── prompts/
    │   └── xx-<name>.<role>
    └── results/
        └── <function>.out
```

The prompts fed to the model at the start of every new conversation are
stored in the `prompts/` directory in the above format. The `results/`
directory contains the function outputs, which can be pasted into the
chat as required. Automatic function execution has not been implemented
since it let me experiment with delayed/partial results, not receiving
the result at all, etc. Once the conversation ends, the messages are
dumped as JSON in the `outputs/` directory.

Pressing enter after a blank line will add your message to the ongoing
conversation. Note that pasting content with blank lines will add
multiple messages to the conversation, with the LLM responding to each
one individually. Press <kbd>ctrl</kbd> + <kbd>c</kbd> to end the chat.
