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
      url "https://github.com/xcrong/pig/releases/download/v1.0.1/pig-macos-arm64.tar.gz"
      sha256 "884c78c6016df096a488976ef7e061a5ddfdfea655817a2bb68e9e3d2d6893de"
    end
  end

  on_linux do
    on_intel do
      url "https://github.com/xcrong/pig/releases/download/v1.0.1/pig-linux-x86_64.tar.gz"
      sha256 "903e8e9e934492dccb36a78a438a1fe49041bb8981aa2ae5f91386a0eceb343f"
    end
  end

  def install
    bin.install "pig"
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/pig --version")
  end
end
