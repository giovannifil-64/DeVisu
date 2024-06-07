# DeVisu

<p align="center">
  <img width="325" src="static/img/DeVisu.svg" alt="DeVisu logo">
</p>

</br>

DeVisu is simple face verification web app that allows users to save, verify, and remove a person from a database, given a face vector.
The application is built with Flask and uses the `face-recognition` library, a python implementation of the dlib face recognition library, to extract face vectors from images.

## Usage

> [!WARNING]
> The application has been with Python 3.11, but it should work with any Python 3.x version.

It's raccomended to use a virtual environment to run the application, in order to avoid conflicts with the system packages.

To create a virtual environment in python, run the following command on macOS and Linux:

```bash
python3 -m venv devisu_env
```

> [!NOTE]
> On Windows, you do not need to specify the python version, so you can run by just typing `python -m venv devisu_env`.

To activate the virtual environment on macOS and Linux, run the following command:

```bash
source devisu_env/bin/activate
```

To activate the virtual environment on Windows:

```bash
devisu_env\Scripts\activate
```

When the virtual environment is activated, you should see the name of the virtual environment in the command line, like this:

```bash
(devisu_env) Path/to/your/folder
```

To install the required packages:

```bash
pip install -r requirements.txt
```

To run the application, type the following command:

```bash
python3 app.py
```

The termianl will display that the application is running on the 0.0.0.0:5000 address, but sometimes it will not work. In this case, try to run the application on the localhost address:

```bash
localhost:5000
```

## License

This project is made available under the Apache 2.0 License - see the [LICENSE](LICENSE.txt) file for details.
