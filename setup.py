from setuptools import setup

setup(
    name="cfnviz",
    version="0.0.1",
    description="Cloudformation template visualization tool",
    url="https://github.com/devquixote/cfnviz",
    author="Lance Woodson",
    author_email="lance.woodson@bazaarvoice.com",
    license="MIT",
    packages=["cfnviz"],
    install_requires=[
      "pyaml",
      "recordclass",
      "twine"
    ],
    scripts=[
      "bin/cfndot",
      "bin/cfnviz"
    ],
    zip_safe=False
)
