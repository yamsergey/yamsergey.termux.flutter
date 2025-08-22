#!/bin/bash

# Create a complete BUILD.gn file for Termux with Android log library support

cat > flutter/engine/src/build/config/termux/BUILD.gn << 'EOF'
import("//build/config/termux/termux.gni")
import("//build/config/sysroot.gni")
import("//build/config/profiler.gni")

config("compiler") {
  if (current_toolchain == "//build/toolchain/termux:${current_cpu}") {
    cflags = [
      "-fno-strict-aliasing",
      "-fstack-protector",
      "--param=ssp-buffer-size=8",
      "-fPIC",
      "-pipe",
      "-fcolor-diagnostics",
      "-ffunction-sections",
      "-funwind-tables",
      "-fno-short-enums",
      "-nostdinc++",
    ]
    cflags_cc = ["-fvisibility-inlines-hidden"]
    cflags_objcc = ["-fvisibility-inlines-hidden"]
    ldflags = [
      "-Wl,--fatal-warnings",
      "-fPIC",
      "-Wl,-z,noexecstack",
      "-Wl,-z,now",
      "-Wl,-z,relro",
      "-Wl,--undefined-version",
      "-Wl,--no-undefined",
      "-Wl,--exclude-libs,ALL",
      "-Wl,--icf=all",
      "-Wl,-z,max-page-size=65536",
    ]
    defines = [
      "__TERMUX__",
      "HAVE_SYS_UIO_H"
    ]
    if (!using_sanitizer) {
      ldflags += [ "-Wl,-z,defs" ]
    }
    if (enable_profiling && !is_debug) {
      defines += [ "ENABLE_PROFILING" ]
      cflags += [
        "-fno-omit-frame-pointer",
        "-mno-omit-leaf-frame-pointer",
        "-g",
      ]
      if (enable_full_stack_frames_for_profiling) {
        cflags += [
          "-fno-inline",
          "-fno-optimize-sibling-calls",
        ]
      }
      ldflags += [ "-rdynamic" ]
    }
    if (using_sanitizer) {
      cflags += [
        "-fno-omit-frame-pointer",
        "-gline-tables-only",
      ]
    }
    if (is_asan) {
      cflags += [ "-fsanitize=address" ]
      ldflags += [ "-fsanitize=address" ]
    }
    if (is_lsan) {
      cflags += [ "-fsanitize=leak" ]
      ldflags += [ "-fsanitize=leak" ]
    }
    if (is_tsan) {
      cflags += [ "-fsanitize=thread" ]
      ldflags += [ "-fsanitize=thread" ]
    }
    if (is_msan) {
      cflags += [ "-fsanitize=memory" ]
      ldflags += [ "-fsanitize=memory" ]
    }
    if (is_ubsan) {
      cflags += [ "-fsanitize=undefined" ]
      ldflags += [ "-fsanitize=undefined" ]
    }
    if (current_cpu == "x64") {
      cflags += [
        "-m64",
        "-march=x86-64",
      ]
      ldflags += [ "-m64" ]
    } else if (current_cpu == "x86") {
      cflags += [ "-m32" ]
      ldflags += [ "-m32" ]
      if (is_clang) {
        cflags += [
          "-mstack-alignment=16",
          "-mstackrealign",
        ]
      }
    } else if (current_cpu == "arm") {
      cflags += [
        "-march=$arm_arch",
        "-mfloat-abi=$arm_float_abi",
      ]
      if (arm_tune != "") {
        cflags += [ "-mtune=$arm_tune" ]
      }
      if (arm_use_thumb) {
        cflags += [ "-mthumb" ]
      }
    }
    if (current_cpu == "arm") {
      cflags += [ "--target=arm-linux-androideabi${termux_api_level}" ]
      ldflags += [ "--target=arm-linux-androideabi${termux_api_level}" ]
    } else if (current_cpu == "arm64") {
      cflags += [ "--target=aarch64-linux-android${termux_api_level}" ]
      ldflags += [ "--target=aarch64-linux-android${termux_api_level}" ]
    } else if (current_cpu == "x86") {
      cflags += [ "--target=i686-linux-androideabi${termux_api_level}" ]
      ldflags += [ "--target=i686-linux-androideabi${termux_api_level}" ]
    } else if (current_cpu == "x64") {
      cflags += [ "--target=x86_64-linux-androideabi${termux_api_level}" ]
      ldflags += [ "--target=x86_64-linux-androideabi${termux_api_level}" ]
    }
    asmflags = cflags
  } else {
    configs = ["//build/config/compiler:compiler"]
  }
}

config("runtime_library") {
  if (current_toolchain == "//build/toolchain/termux:${current_cpu}") {
    cflags_cc = ["-nostdinc++"]
    cflags_objcc = [ "-nostdinc++" ]
    defines = [
      "__compiler_offsetof=__builtin_offsetof",
      "nan=__builtin_nan"
    ]
    ldflags = [
      "-stdlib=libstdc++",
      "-Wl,--warn-shared-textrel"
    ]
    lib_dirs = [ "$custom_toolchain/lib/clang/19/lib/linux/" ]
    include_dirs = [
      "//flutter/third_party/libcxx/include",
      "//flutter/third_party/libcxxabi/include",
    ]
  } else {
    configs = ["//build/config/compiler:runtime_library"]
  }
}

config("executable_ldconfig") {
  if (current_toolchain == "//build/toolchain/termux:${current_cpu}") {
    ldflags = [
      "-Bdynamic",
      "-Wl,-z,nocopyreloc",
    ]
  } else {
    configs = ["//build/config/gcc:executable_ldconfig"]
  }
}

config("sdk") {
  cflags = []
  ldflags = [ "-Wl,-rpath=/data/data/com.termux/files/usr/lib" ]
  libs = [ "log" ]
  lib_dirs = [ "$custom_toolchain/lib/clang/19/lib/linux/" ]
  if (defined(target_sysroot) && target_sysroot != "") {
    cflags += [ "--sysroot=" + target_sysroot ]
    ldflags += [ "--sysroot=" + target_sysroot ]
  }
  if (defined(custom_sysroot) && custom_sysroot != "") {
    cflags += [ "-idirafter$custom_sysroot/usr/include" ]
    lib_dirs += [ "$custom_sysroot/usr/lib" ]
  }
}
EOF

echo "BUILD.gn file created successfully"
echo "File has $(wc -l < flutter/engine/src/build/config/termux/BUILD.gn) lines"
echo "=== Last 5 lines ==="
tail -5 flutter/engine/src/build/config/termux/BUILD.gn | cat -n