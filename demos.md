# Curiosity Toolkit Demos

This document describes how to setup and initialise our demos applications included
in our _curiosity toolkit_:

1. [The Learning Machine](#setup-the-learning-machine)

First of all, it is necessary to setup the required **environment**. To do so, 
please read instructions reported in the technical documentation 
[here](./docs/setup_env.md).


### Setup the Learning Machine

The _learning machine_ is composed by a _frontend_ component, and a _backend_ component.
The two components have to be executed both in order to make the demo working. 

(a) To run the `backend` it is just necessary to execute the `app.py` file, 
located in the main folder of the _backend_ component, i.e. `learning_machine/backend`:

```shell script
python app.py
```

This will run the backend webserver on the `localhost` address (i.e. `127.0.0.1`), 
and port `8000`.

Alternatively, it is also possible to run the webserver directly running the 
`uvicorn` server, with the following command: 

```shell script
uvicorn app:learning_machine_backend --reload
```

(b) The frontend is a simple HTML application, that requires an `HTTP` server to run. 
The easiest and quickest way to do this, is to execute the following command in 
a Terminal while in the `frontend` main folder, i.e. `learning_machine/frontend`:
```shell script
python -m http.server 8282 --bind 127.0.0.1
```

This will run a simple HTTP webserver on the port `8282` and `localhost` address.


#### Testing the components up-and-running

To test the _backend_ component, it is necessary to navigate the following address
into a browser window: 

- [`localhost:8000/docs`](http://localhost:8000/docs)

If all is working, you should be able to access the Swagger API documentation page.

Similarly, to test that also the _frontend_ component is correctly setup and running,
please navigate the following address into a browser window: 

- [`localhost:8282/learning_machine.html`](http://localhost:8282/learning_machine.html)

 **Note**: This path assumes that the previous command to run the `http` Python server
 has been run within the `frontend` main folder.
