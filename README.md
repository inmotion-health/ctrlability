# CTRLABILITY

⚠️ **This project is still in development and not ready for use.**

Many traditional input methods for computers are inaccessible. People with motor disabilities can experience major hurdles when using mice, keyboards or game controllers. This often means that those affected are restricted in their digital participation - they cannot interact with or communicate via digital media like others.

The project uses the combination of microphone and webcam to translate gestures, movements and voice commands into control commands for a computer. This breaks down barriers between patients and medical staff and allows new therapeutic approaches to be developed or supported.

To read more, see the [project website](https://prototypefund.de/project/ctrlability-kontroller-fuer-menschen-mit-motorischen-einschraenkungen/) at the Prototype Fund.

## Building

To build the project you need to have a current C++ compiler and CMake installed. All other dependencies are downloaded and built automatically.

To build the project, run the following commands:

```bash
pip install -r requirements.txt
conan profile detect
sh build.sh
```

## Running

To run the project, run the following command:

```bash
python /src/main.py
```

## License

This project is licensed under the MIT license. See the [LICENSE](LICENSE) file for details.
