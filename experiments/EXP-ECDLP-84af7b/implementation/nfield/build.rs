fn main() {
    #[cfg(feature = "pari")]
    {
        println!("cargo:rerun-if-changed=csrc/pari_shim.c");
        cc::Build::new()
            .file("csrc/pari_shim.c")
            .include("/usr/include/x86_64-linux-gnu")
            .include("/usr/include")
            .compile("pari_shim");
        println!("cargo:rustc-link-lib=pari");
        println!("cargo:rustc-link-lib=gmp");
    }
}
