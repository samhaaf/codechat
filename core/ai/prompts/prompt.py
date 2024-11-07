class Prompt:
    def __init__(self):
        self.prompt_components = []

    def add_component(self, component):
        self.prompt_components.append(component)

    def render(self):
        return "\n".join(str(component) for component in self.prompt_components)

    @classmethod
    def from_cli(cls):
        return cls()

    def __str__(self):
        return self.render()
