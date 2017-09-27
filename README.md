# What is Fenix?

Fenix is a tool to produce core-dumps that are compatible with python debugger tools when your code raises an uncaught exception. Fenix only works when this happens and therefore there is no runtime overhead associated with the tool. There are many ways available to trigger this behaviour depending on the granularity that you want. These can be as little invasive as running your code though a runner (and therefore you don’t need to change yor code) or as granular as context managers and decorators (so you can generate these core dumps for specific parts of your code).

![fenix live](docs/images/fenix.gif)

# How to use Fenix?

Check the [documentation](https://bbgithub.dev.bloomberg.com/pages/pgalindo3/fenix/)
