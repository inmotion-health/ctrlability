# CTRLABILITY

⚠️ **This project is still in development and not ready for use.** ⚠️

Many traditional input methods for computers are inaccessible. People with motor disabilities can experience major hurdles when using mice, keyboards or game controllers. This often means that those affected are restricted in their digital participation - they cannot interact with or communicate via digital media like others.

The project uses the combination of microphone and webcam to translate gestures, movements and voice commands into control commands for a computer. This breaks down barriers between patients and medical staff and allows new therapeutic approaches to be developed or supported.

To read more, see the [project website](https://prototypefund.de/project/ctrlability-kontroller-fuer-menschen-mit-motorischen-einschraenkungen/) at the Prototype Fund.

## Usage

To use this project, you first need to install all our dependencies. You can do this by running the following command. We recommend using a virtual environment, such as [venv](https://docs.python.org/3/library/venv.html) or [conda](https://docs.conda.io/en/latest/), as well as Python 3.10 or higher (currently >=3.12 is not supported), also you need to have `ffmpeg` installed and added to your path.

```bash
pip install .
# or us the -e flag so you can use and develop at the same time, without the need to reinstall https://stackoverflow.com/questions/42609943/what-is-the-use-case-for-pip-install-e
pip install -e . 
```

Afterwards, you can start the application by running the following command:  
(first startup can take a few seconds)

```bash
python -m ctrlability
```

## Documentation

This project is still in rapid and early development. As such, the documentation is not yet complete or may not be fully up to date. However, we are working on it. You can find the documentation in the [`docs`](docs) folder. The following documentation is currently available:

1. [Command Line Arguments](docs/arguments.md)
2. [General Architecture](docs/architecture.md)
3. **Available Components**
   1. [Streams](docs/streams.md)
   2. [Processors](docs/processors.md)
   3. [Triggers](docs/triggers.md)
   4. [Actions](docs/actions.md)

## License

This project is licensed under the MIT license. See the [LICENSE](LICENSE) file for details.
