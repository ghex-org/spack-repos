from spack.package import *


class Ghex(CMakePackage, CudaPackage, ROCmPackage):
    """GHEX is a generic halo-exchange library."""

    homepage = "https://github.com/ghex-org/GHEX"
    url = "https://github.com/ghex-org/GHEX/archive/refs/tags/v0.3.0.tar.gz"
    git = "https://github.com/ghex-org/GHEX.git"
    maintainers = ["boeschf"]

    version("0.4.1", tag="v0.4.1", submodules=True)
    version("0.4.0", tag="v0.4.0", submodules=True)
    version("0.3.0", tag="v0.3.0", submodules=True)
    version("master", branch="master", submodules=True)

    depends_on("cxx", type="build")

    generator("ninja")

    backends = ("mpi", "ucx", "libfabric")
    variant(
        "backend", default="mpi", description="Transport backend", values=backends, multi=False
    )
    variant("xpmem", default=False, description="Use xpmem shared memory")
    variant("python", default=True, description="Build Python bindings")

    depends_on("cmake@3.21:", type="build")
    depends_on("mpi")
    depends_on("boost")
    depends_on("xpmem", when="+xpmem", type=("build", "run"))

    depends_on("oomph")
    for backend in backends:
        depends_on(f"oomph backend={backend}", when=f"backend={backend}")
    depends_on("oomph+cuda", when="+cuda")
    depends_on("oomph+rocm", when="+rocm")
    depends_on("oomph@0.3:", when="@0.3:")

    conflicts("+cuda+rocm")

    with when("+python"):
        extends("python")
        depends_on("python@3.7:", type="build")
        depends_on("py-pip", type="build")
        depends_on("py-pybind11", type="build")
        depends_on("py-mpi4py", type=("build", "run"))
        depends_on("py-numpy", type=("build", "run"))

        depends_on("py-pytest", when="+python", type=("test"))

    def cmake_args(self):
        spec = self.spec

        args = [
            self.define("GHEX_USE_BUNDLED_LIBS", True),
            self.define("GHEX_USE_BUNDLED_GRIDTOOLS", True),
            self.define("GHEX_USE_BUNDLED_GTEST", self.run_tests),
            self.define("GHEX_USE_BUNDLED_OOMPH", False),
            self.define("GHEX_TRANSPORT_BACKEND", spec.variants["backend"].value.upper()),
            self.define_from_variant("GHEX_USE_XPMEM", "xpmem"),
            self.define_from_variant("GHEX_BUILD_PYTHON_BINDINGS", "python"),
            self.define("GHEX_WITH_TESTING", self.run_tests),
        ]

        if spec.satisfies("+python"):
            args.append(self.define("GHEX_PYTHON_LIB_PATH", python_platlib))

        if self.run_tests and spec.satisfies("^openmpi"):
            args.append(self.define("MPIEXEC_PREFLAGS", "--oversubscribe"))

        if "+cuda" in spec and spec.variants["cuda_arch"].value != "none":
            arch_str = ";".join(spec.variants["cuda_arch"].value)
            args.append(self.define("CMAKE_CUDA_ARCHITECTURES", arch_str))
            args.append(self.define("GHEX_USE_GPU", True))
            args.append(self.define("GHEX_GPU_TYPE", "CUDA"))

        if "+rocm" in spec and spec.variants["amdgpu_target"].value != "none":
            arch_str = ";".join(spec.variants["amdgpu_target"].value)
            args.append(self.define("CMAKE_HIP_ARCHITECTURES", arch_str))
            args.append(self.define("GHEX_USE_GPU", True))
            args.append(self.define("GHEX_GPU_TYPE", "AMD"))

        if spec.satisfies("~cuda~rocm"):
            args.append(self.define("GHEX_USE_GPU", False))

        return args
