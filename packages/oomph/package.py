from spack.package import *

class Oomph(CMakePackage, CudaPackage, ROCmPackage):
    """"Oomph is a non-blocking callback-based point-to-point communication library."""

    homepage="https://github.com/ghex-org/oomph"
    url = "https://github.com/ghex-org/oomph/archive/refs/tags/v0.2.0.tar.gz"
    git = "https://github.com/ghex-org/oomph.git"
    maintainers = ["boeschf"]

    version("0.2.0", sha256="135cdb856aa817c053b6af1617869dbcd0ee97d34607e78874dd775ea389434e", submodules=True)
    version("0.1.0", sha256="0ff36db0a5f30ae1bb02f6db6d411ea72eadd89688c00f76b4e722bd5a9ba90b", submodules=True)
    version("main", branch="main", submodules=True)
    # for dev-build
    version("develop")
    
    variant(
        "backend", default="mpi", description="Transport backend",
        values=("mpi", "ucx", "libfabric"), multi=False)

    variant("fortran-bindings", default=False, description="Build Fortran bindings")
    with when("+fortran-bindings"):
        variant("fortran-fp", default="float", description="Floating point type", values=("float", "double"), multi=False)
        variant("fortran-openmp", default=True, description="Compile with OpenMP")

    variant("enable-barrier", default=True, description="Enalbe thread barrier (disable for task based runtime)")

    depends_on("hwmalloc+cuda", when="+cuda")
    depends_on("hwmalloc+rocm", when="+rocm")
    depends_on("hwmalloc", when="~cuda~rocm")

    with when("backend=ucx"):
        depends_on("ucx+cuda", when="+cuda")
        depends_on("ucx+rocm", when="+rocm")
        depends_on("ucx", when="~cuda~rocm")
        variant("use-pmix", default="False",
            description="Use PMIx to establisch out-of-band setup")
        variant("use-spin-lock", default="False",
            description="Use pthread spin locks")
        depends_on("pmix", when="+use-pmix")

    with when("backend=libfabric"):
        variant("libfabric-provider", default="tcp", description="fabric", values=("cxi", "gni", "psm2", "sockets", "tcp", "verbs"), multi=False)
        depends_on("libfabric fabrics=cxi", when="libfabric-provider=cxi")
        depends_on("libfabric fabrics=gni", when="libfabric-provider=gni")
        depends_on("libfabric fabrics=psm2", when="libfabric-provider=psm2")
        depends_on("libfabric fabrics=sockets", when="libfabric-provider=sockets")
        depends_on("libfabric fabrics=tcp", when="libfabric-provider=tcp")
        depends_on("libfabric fabrics=verbs", when="libfabric-provider=verbs")

    depends_on("mpi")
    depends_on("boost")

    def cmake_args(self):
        args = [
            self.define_from_variant("OOMPH_BUILD_FORTRAN", "fortran-bindings"),
            self.define_from_variant("OOMPH_FORTRAN_OPENMP", "fortran-openmp"),
            self.define_from_variant("OOMPH_UCX_USE_PMI", "use-pmix"),
            self.define_from_variant("OOMPH_UCX_USE_SPIN_LOCK", "use-spin-lock"),
            self.define_from_variant("OOMPH_ENABLE_BARRIER", "enable-barrier"),
            self.define("OOMPH_WITH_TESTING", self.run_tests),
            self.define("OOMPH_GIT_SUBMODULE", False),
            self.define("OOMPH_USE_BUNDLED_LIBS", False),
        ]

        if self.run_tests:
            self.define("MPIEXEC_PREFLAGS", "--oversubscribe")

        if self.spec.variants["fortran-bindings"].value == True:
            if self.spec.variants["fortran-fp"].value == "float":
                args.append("-DOOMPH_FORTRAN_FP=float")
            else:
                args.append("-DOOMPH_FORTRAN_FP=double")

        if self.spec.variants["backend"].value == "ucx":
            args.append("-DOOMPH_WITH_MPI=OFF")
            args.append("-DOOMPH_WITH_UCX=ON")
            args.append("-DOOMPH_WITH_LIBFABRIC=OFF")
        elif self.spec.variants["backend"].value == "libfabric":
            args.append("-DOOMPH_WITH_MPI=OFF")
            args.append("-DOOMPH_WITH_UCX=OFF")
            args.append("-DOOMPH_WITH_LIBFABRIC=ON")
        else:
            args.append("-DOOMPH_WITH_MPI=ON")
            args.append("-DOOMPH_WITH_UCX=OFF")
            args.append("-DOOMPH_WITH_LIBFABRIC=OFF")

        if "libfabric-provider=verbs" in self.spec:
            args.append("-DOOMPH_LIBFABRIC_PROVIDER=verbs")
        elif "libfabric-provider=gni" in self.spec:
            args.append("-DOOMPH_LIBFABRIC_PROVIDER=gni")
        elif "libfabric-provider=cxi" in self.spec:
            args.append("-DOOMPH_LIBFABRIC_PROVIDER=cxi")
        elif "libfabric-provider=tcp" in self.spec:
            args.append("-DOOMPH_LIBFABRIC_PROVIDER=tcp")
        elif "libfabric-provider=sockets" in self.spec:
            args.append("-DOOMPH_LIBFABRIC_PROVIDER=sockets")
        elif "libfabric-provider=pwm2" in self.spec:
            args.append("-DOOMPH_LIBFABRIC_PROVIDER=psm2")

        return args
