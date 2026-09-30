class Pig < Formula
  desc "Grok Build with Providers"
  homepage "https://github.com/xcrong/pig"
  license "Apache-2.0"

  livecheck do
    url :homepage
    strategy :github_latest
  end

  on_macos do
    on_arm do
      url "https://github.com/xcrong/pig/releases/download/v1.1.0/pig-macos-arm64.tar.gz"
      sha256 "d353761c38db77a1b42d3839a0890cd6adef8b088ee507b0539dd17992620aea"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/xcrong/pig/releases/download/v1.1.0/pig-linux-x86_64.tar.gz"
      sha256 "316619ced78a45a9bbd19bc135ff65ff9586138581c3df23619a4fc0c37835a2"
    end
  end

  def install
    bin.install "pig"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/pig --version")
  end
end
