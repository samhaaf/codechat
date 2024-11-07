A command-line tool for software development LLM workflows.


## Installation

```
git clone https://www.github.com/samhaaf/codechat
cd codechat
pip install
```


## Usage

All positional args are files to include, and you can specify the model with --model or -m.

For example:

```
codechat --model o1-mini my_project/
|     ___          _        ___ _           _
|    / __\___   __| | ___  / __\ |__   __ _| |_
|   / /  / _ \ / _` |/ _ \/ /  | '_ \ / _` | __|
|  / /__| (_) | (_| |  __/ /___| | | | (_| | |_
|  \____/\___/ \__,_|\___\____/|_| |_|\__,_|\__|
|  ---------------------------------------------
|- New session with model `o1-mini`..
|- Included files:
   |- my_project/
   |  |- folder1/
   |  |  |- file1_zab24n.txt
   |  |- folder2/
   |  |  |- file2_OxgUK8.txt
   |  |- folder3/
   |  |  |- file3_xrlfWT.txt
|<
```

### Multiline Inputs

In order to give multi-line inputs, you need to start and end with a control character: `!@#`. (shift-1-2-3)

```
|< Here's what I think we should do: !@#
- Update this
- Update that
!@#
|- Awaiting response.. (0.0s)
```

### Exclusions

You can exclude files that match pathspec patterns by introducing a .gptignore file. For example:

```
# ./.gptignore
**/*.png
**/*.bin
my_secrets/
```


## Roadmap

- [ ] Apply changes directly to files 
- [ ] Multi-agent workflows
