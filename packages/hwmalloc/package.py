from spack.package import *

class Hwmalloc(CMakePackage, CudaPackage, ROCmPackage):
    """"HWMALLOC is a allocator which supports memory registration for e.g. remote memory access"""

    homepage="https://github.com/ghex-org/hwmalloc"
    git = "https://github.com/ghex-org/hwmalloc.git"
    maintainers = ["boeschf"]

    version("0.2.0", sha256="734758a390a3258b86307e4aef50a7ca2e5d0e2e579f18aeefcd05397e114419")
    version("0.1.0", sha256="06e9bfcef0ecce4d19531ccbe03592b502d1281c7a092bc0ff51ca187899b21c")
    version("master", branch="master")

    depends_on("numactl", type=("build", "run"))
    depends_on("boost", type=("build"))

    variant("numa-throws", default=False, description="True if numa_tools may throw during initialization")
    variant("numa-local", default=True, description="Use numa_tools for local node allocations")
    variant("logging", default=False, description="print logging info to cerr")

    def cmake_args(self):
        args = [
            self.define_from_variant("HWMALLOC_NUMA_THROWS", "numa-throws"),
            self.define_from_variant("HWMALLOC_NUMA_FOR_LOCAL", "numa-local"),
            self.define_from_variant("HWMALLOC_ENABLE_LOGGING", "logging"),
        ]

        if "+cuda" in self.spec:
            args.append("-DHWMALLOC_ENABLE_DEVICE=ON")
            args.append("-DHWMALLOC_DEVICE_RUNTIME=cuda")
        elif "+rocm" in self.spec:
            args.append("-DHWMALLOC_ENABLE_DEVICE=ON")
            args.append("-DHWMALLOC_DEVICE_RUNTIME=hip")

        return args
