import os
import json
import ollama

from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from rich.text import Text
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from rich import print as rprint

console = Console()

def display_banner():
    banner = Text("function calling experiments", style="bold bright_blue")
    console.print(Panel(banner, style="bright_blue", padding=(1, 2)))
    console.print()

def load_prompts(experiment_path):
    messages = []

    with console.status("[bold green]loading experiment files...", spinner="dots"):
        for file in sorted(os.listdir(f"{experiment_path}/prompts")):
            if "." in file:
                _, role = file.split(".", 1)
                file_path = f"{experiment_path}/prompts/{file}"

                try:
                    with open(file_path) as f:
                        content = f.read()
                        messages.append({"role": role, "content": content})
                except Exception as e:
                    console.print(f"failed to load {file}: {e}", style="red")

    return messages

def format_response(content, model_name):
    if any(marker in content for marker in ['#', '*', '```', '`', '-', '1.']):
        try:
            return Markdown(content)
        except:
            pass

    return Panel(
        content,
        title=f"{model_name}",
        title_align="left",
        border_style="blue",
        padding=(1, 2)
    )

def get_multiline_input():
    console.print("[bold green]you[/bold green] (type your message, press ctrl+d when done):")
    lines = []

    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass

    return '\n'.join(lines)

def main():
    display_banner()

    experiments_dir = "experiments"
    if not os.path.exists(experiments_dir):
        console.print(f"experiments directory '{experiments_dir}' not found!", style="red bold")
        return

    experiments = [d for d in os.listdir(experiments_dir)
                  if os.path.isdir(os.path.join(experiments_dir, d))]
    if not experiments:
        console.print("no experiments found in experiments directory", style="yellow")
        return

    console.print("[bold cyan]available experiments:[/bold cyan]")
    for i, exp in enumerate(experiments, 1):
        console.print(f"  {i}. {exp}")
    console.print()

    choice = IntPrompt.ask(
        "[bold cyan]select experiment[/bold cyan]",
        choices=[str(i) for i in range(1, len(experiments) + 1)],
        console=console
    )
    experiment_name = experiments[choice - 1]
    experiment_path = f"experiments/{experiment_name}"

    messages = load_prompts(experiment_path)
    if not messages:
        console.print("no valid message files found in experiment directory", style="yellow")
        return
    console.print(f"loaded {len(messages)} message(s) from experiment")

    model = "gemma3:27b"
    agent = ollama.Client()

    console.print(f"connected to [bold green]{model}[/bold green]\n")

    try:
        while True:
            user_message = get_multiline_input()
            if user_message.strip() == "":
                continue

            messages.append({"role": "user", "content": user_message})
            try:
                content = ""
                console.print(f"[bold blue]{model}[/bold blue] (the response will be streamed):")

                with Live(console=console, refresh_per_second=10) as live:
                    for chunk in agent.chat(model=model, messages=messages, stream=True):
                        if 'message' in chunk and 'content' in chunk['message']:
                            chunk_content = chunk['message']['content']
                            content += chunk_content

                            try:
                                live.update(Markdown(content))
                            except:
                                live.update(content)

                console.print()

                if content.strip():
                    messages.append({"role": "assistant", "content": content})
                else:
                    console.print("no content received from model", style="red")

            except Exception as e:
                console.print(f"\nerror getting response: {e}", style="red bold")
                continue

            console.print()

    except KeyboardInterrupt:
        console.print("\ngoodbye!", style="bold yellow")
    except Exception as e:
        console.print(f"\nunexpected error: {e}", style="red bold")

    finally:
        timestamp = datetime.now().replace(microsecond=0).isoformat().replace(":", "-")
        with open(f"{experiment_path}/outputs/{timestamp}.json", "w") as f:
            json.dump(messages, f, indent = 2)

if __name__ == "__main__":
    main()
