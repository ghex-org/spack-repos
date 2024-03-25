from spack.package import *

class Ghex(CMakePackage, CudaPackage, ROCmPackage):
    """"GHEX is a generic halo-exchange library."""

    homepage="https://github.com/ghex-org/GHEX"
    url = "https://github.com/ghex-org/GHEX/archive/refs/tags/v0.3.0.tar.gz"
    
    git = "https://github.com/ghex-org/GHEX.git"
    maintainers = ["boeschf"]

    version("0.4.0", tag="v0.4.0", submodules=True)
    version("0.3.0", tag="v0.3.0", submodules=True)
    # for dev-build
    version("develop")

    variant("xpmem", default=False, description="Use xpmem shared memory")
    variant("python", default=True, description="Build Python bindings")

    depends_on("cmake@3.21:")
    depends_on("mpi")
    depends_on("boost")
    depends_on("xpmem", when="+xpmem", type=("build", "run"))
    depends_on("googletest", type="test")

    depends_on("oomph")
    depends_on("oomph+cuda", when="+cuda")
    depends_on("oomph+rocm", when="+rocm")
    depends_on("oomph@0.3:", when="@0.3:")

    extends("python", when="+python")
    depends_on("python@3.7:", when="+python", type="build")
    depends_on("py-pip", when="+python", type="build")
    depends_on("py-pybind11", when="+python", type="build")
    depends_on("py-mpi4py", when="+python", type=("build", "run"))
    depends_on("py-numpy", when="+python", type=("build", "run"))

    depends_on("py-pytest", when="+python", type=("test"))

    def cmake_args(self):
        spec = self.spec

        if spec["oomph"].satisfies("backend=ucx", False):
            backend = "UCX"
        elif spec["oomph"].satisfies("backend=libfabric", False):
            backend = "LIBFABRIC"
        else:
            backend = "MPI"

        pyexe = spec["python"].command.path

        args = [
            self.define("GHEX_USE_BUNDLED_LIBS", True),
            self.define("GHEX_USE_BUNDLED_GRIDTOOLS", True),
            self.define("GHEX_USE_BUNDLED_OOMPH", False),
            self.define("GHEX_USE_BUNDLED_GTEST", False),
            self.define("GHEX_TRANSPORT_BACKEND", backend),
            self.define_from_variant("GHEX_USE_XPMEM", "xpmem"),
            self.define_from_variant("GHEX_BUILD_PYTHON_BINDINGS", "python"),
            self.define("GHEX_PYTHON_LIB_PATH", python_platlib),
            self.define("GHEX_WITH_TESTING", self.run_tests),
            self.define("MPIEXEC_PREFLAGS", "--oversubscribe"),
        ]

        if self.run_tests:
            args.append("-DMPIEXEC_PREFLAGS=--oversubscribe")

        return args
        
