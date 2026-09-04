"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

const API_BASE_URL = "http://127.0.0.1:8000";

export default function Home() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    setError("");
    setSuccess("");
    setIsLoading(true);

    try {
      const formData = new URLSearchParams();

      // FastAPI OAuth2PasswordRequestForm expects "username"
      // even though our application uses email for login.
      formData.append("username", email.trim());
      formData.append("password", password);

      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
        body: formData.toString(),
      });

      const data = await response.json();

      if (!response.ok) {
        let message = "Unable to sign in. Please check your credentials.";

        if (typeof data?.detail === "string") {
          message = data.detail;
        }

        throw new Error(message);
      }

      if (!data?.access_token) {
        throw new Error("Login succeeded, but no access token was returned.");
      }

      // Remember Me = persistent storage
      // Otherwise token lives only for this browser tab/session.
      if (rememberMe) {
        localStorage.setItem("treeflow_access_token", data.access_token);
        localStorage.setItem(
          "treeflow_token_type",
          data.token_type || "bearer"
        );

        sessionStorage.removeItem("treeflow_access_token");
        sessionStorage.removeItem("treeflow_token_type");
      } else {
        sessionStorage.setItem("treeflow_access_token", data.access_token);
        sessionStorage.setItem(
          "treeflow_token_type",
          data.token_type || "bearer"
        );

        localStorage.removeItem("treeflow_access_token");
        localStorage.removeItem("treeflow_token_type");
      }

      setSuccess("Login successful. Opening your workspace...");

      // Dashboard page will be created next.
      setTimeout(() => {
        router.push("/dashboard");
      }, 500);
    } catch (err) {
      if (err instanceof TypeError) {
        setError(
          "Cannot connect to the TreeFlow AI backend. Make sure the FastAPI server is running."
        );
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong while signing in.");
      }
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f5f7fb]">
      <div className="grid min-h-screen lg:grid-cols-2">
        {/* Left Section */}
        <section className="relative hidden overflow-hidden bg-[#101828] p-12 text-white lg:flex lg:flex-col lg:justify-between">
          <div className="absolute -left-40 -top-40 h-96 w-96 rounded-full bg-blue-500/20 blur-3xl" />
          <div className="absolute -bottom-40 right-0 h-96 w-96 rounded-full bg-purple-500/20 blur-3xl" />

          <div className="relative z-10">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600 text-xl font-bold shadow-lg shadow-blue-900/30">
                T
              </div>

              <div>
                <h1 className="text-xl font-bold">TreeFlow AI</h1>
                <p className="text-sm text-slate-400">
                  Smart Work Management
                </p>
              </div>
            </div>
          </div>

          <div className="relative z-10 max-w-xl">
            <span className="mb-5 inline-flex rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm text-blue-200">
              AI-powered productivity platform
            </span>

            <h2 className="text-5xl font-bold leading-tight tracking-tight">
              Manage your work.
              <br />
              <span className="text-blue-400">Smarter and faster.</span>
            </h2>

            <p className="mt-6 max-w-lg text-lg leading-8 text-slate-300">
              Organize projects, collaborate with your team, manage tasks,
              files, notifications and workflows from one intelligent
              workspace.
            </p>

            <div className="mt-10 grid grid-cols-3 gap-4">
              <FeatureCard number="01" title="Projects" />
              <FeatureCard number="02" title="Smart Tasks" />
              <FeatureCard number="03" title="AI Insights" />
            </div>
          </div>

          <div className="relative z-10 text-sm text-slate-500">
            © 2026 TreeFlow AI. All rights reserved.
          </div>
        </section>

        {/* Login Section */}
        <section className="flex min-h-screen items-center justify-center px-6 py-12 sm:px-10">
          <div className="w-full max-w-md">
            {/* Mobile Logo */}
            <div className="mb-10 lg:hidden">
              <div className="flex items-center gap-3">
                <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600 text-xl font-bold text-white">
                  T
                </div>

                <div>
                  <h1 className="text-xl font-bold text-slate-900">
                    TreeFlow AI
                  </h1>
                  <p className="text-sm text-slate-500">
                    Smart Work Management
                  </p>
                </div>
              </div>
            </div>

            <div className="mb-8">
              <p className="mb-2 text-sm font-semibold text-blue-600">
                WELCOME BACK
              </p>

              <h2 className="text-3xl font-bold tracking-tight text-slate-900">
                Sign in to your account
              </h2>

              <p className="mt-3 text-sm leading-6 text-slate-500">
                Enter your credentials to access your TreeFlow AI workspace.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              {/* Email */}
              <div>
                <label
                  htmlFor="email"
                  className="mb-2 block text-sm font-semibold text-slate-700"
                >
                  Email address
                </label>

                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(event) => setEmail(event.target.value)}
                  placeholder="you@example.com"
                  required
                  disabled={isLoading}
                  autoComplete="email"
                  className="h-12 w-full rounded-xl border border-slate-200 bg-white px-4 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 disabled:cursor-not-allowed disabled:bg-slate-100"
                />
              </div>

              {/* Password */}
              <div>
                <div className="mb-2 flex items-center justify-between">
                  <label
                    htmlFor="password"
                    className="block text-sm font-semibold text-slate-700"
                  >
                    Password
                  </label>

                  <button
                    type="button"
                    className="text-sm font-semibold text-blue-600 transition hover:text-blue-700"
                  >
                    Forgot password?
                  </button>
                </div>

                <div className="relative">
                  <input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    value={password}
                    onChange={(event) => setPassword(event.target.value)}
                    placeholder="Enter your password"
                    required
                    disabled={isLoading}
                    autoComplete="current-password"
                    className="h-12 w-full rounded-xl border border-slate-200 bg-white px-4 pr-20 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 disabled:cursor-not-allowed disabled:bg-slate-100"
                  />

                  <button
                    type="button"
                    onClick={() => setShowPassword((current) => !current)}
                    disabled={isLoading}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-sm font-semibold text-slate-500 transition hover:text-slate-800 disabled:cursor-not-allowed"
                  >
                    {showPassword ? "Hide" : "Show"}
                  </button>
                </div>
              </div>

              {/* Remember Me */}
              <div className="flex items-center gap-3">
                <input
                  id="remember"
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(event) => setRememberMe(event.target.checked)}
                  disabled={isLoading}
                  className="h-4 w-4 rounded border-slate-300 accent-blue-600"
                />

                <label
                  htmlFor="remember"
                  className="text-sm text-slate-600"
                >
                  Remember me
                </label>
              </div>

              {/* Error */}
              {error && (
                <div
                  role="alert"
                  className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm leading-6 text-red-700"
                >
                  {error}
                </div>
              )}

              {/* Success */}
              {success && (
                <div
                  role="status"
                  className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm leading-6 text-emerald-700"
                >
                  {success}
                </div>
              )}

              {/* Submit */}
              <button
                type="submit"
                disabled={isLoading}
                className="flex h-12 w-full items-center justify-center rounded-xl bg-blue-600 px-5 text-sm font-semibold text-white shadow-lg shadow-blue-600/20 transition hover:bg-blue-700 active:scale-[0.99] disabled:cursor-not-allowed disabled:bg-blue-400 disabled:active:scale-100"
              >
                {isLoading ? (
                  <span className="flex items-center gap-3">
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
                    Signing in...
                  </span>
                ) : (
                  "Sign In"
                )}
              </button>
            </form>

            <div className="mt-8 flex items-center gap-4">
              <div className="h-px flex-1 bg-slate-200" />

              <span className="text-xs font-medium uppercase tracking-wider text-slate-400">
                Secure Workspace
              </span>

              <div className="h-px flex-1 bg-slate-200" />
            </div>

            <div className="mt-8 rounded-xl border border-slate-200 bg-white p-4">
              <p className="text-center text-sm leading-6 text-slate-500">
                TreeFlow AI keeps your workspace protected with secure
                authentication and role-based access.
              </p>
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}

function FeatureCard({
  number,
  title,
}: {
  number: string;
  title: string;
}) {
  return (
    <div className="rounded-2xl border border-white/10 bg-white/5 p-4 backdrop-blur">
      <p className="text-xs font-semibold text-blue-400">{number}</p>
      <p className="mt-2 text-sm font-medium text-slate-200">{title}</p>
    </div>
  );
}