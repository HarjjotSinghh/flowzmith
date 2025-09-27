import { useState } from "react";
import { Code, LogIn } from "lucide-react";
import useAuth from "@/utils/useAuth";

export default function SignIn() {
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const { signInWithCredentials } = useAuth();

  const onSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    if (!email || !password) {
      setError("Please fill in all fields");
      setLoading(false);
      return;
    }

    try {
      await signInWithCredentials({
        email,
        password,
        callbackUrl: "/",
        redirect: true,
      });
    } catch (err) {
      const errorMessages = {
        OAuthSignin: "Couldn't start sign-in. Please try again or use a different method.",
        OAuthCallback: "Sign-in failed after redirecting. Please try again.",
        OAuthCreateAccount: "Couldn't create an account with this sign-in method. Try another option.",
        EmailCreateAccount: "This email can't be used to create an account. It may already exist.",
        Callback: "Something went wrong during sign-in. Please try again.",
        OAuthAccountNotLinked: "This account is linked to a different sign-in method. Try using that instead.",
        CredentialsSignin: "Incorrect email or password. Try again or reset your password.",
        AccessDenied: "You don't have permission to sign in.",
        Configuration: "Sign-in isn't working right now. Please try again later.",
        Verification: "Your sign-in link has expired. Request a new one.",
      };

      setError(errorMessages[err.message] || "Something went wrong. Please try again.");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F3F3F3] dark:bg-[#0A0A0A] flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] rounded-full mb-4">
            <Code size={24} className="text-white" />
          </div>
          <h1 className="text-2xl font-bold text-black dark:text-white font-sora">
            Web3 dApp Builder
          </h1>
          <p className="text-[#6F6F6F] dark:text-[#AAAAAA] mt-2">
            Sign in to your account
          </p>
        </div>

        {/* Form */}
        <form onSubmit={onSubmit} className="bg-white dark:bg-[#1E1E1E] rounded-xl border border-[#E6E6E6] dark:border-[#333333] p-6 shadow-lg">
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-[#4D4D4D] dark:text-[#B0B0B0] mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter your email"
                className="w-full px-4 py-3 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white placeholder-[#6B7280] dark:placeholder-[#999999] focus:border-[#6366F1] dark:focus:border-[#6366F1] transition-colors"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[#4D4D4D] dark:text-[#B0B0B0] mb-2">
                Password
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                className="w-full px-4 py-3 border border-[#D1D5DB] dark:border-[#404040] rounded-lg bg-white dark:bg-[#262626] text-black dark:text-white placeholder-[#6B7280] dark:placeholder-[#999999] focus:border-[#6366F1] dark:focus:border-[#6366F1] transition-colors"
                required
              />
            </div>

            {error && (
              <div className="p-4 bg-[#FEF2F2] dark:bg-[#4C1D1D] border border-[#FECACA] dark:border-[#F87171] rounded-lg">
                <p className="text-sm text-[#DC2626] dark:text-[#F87171]">{error}</p>
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-b from-[#6366F1] to-[#4F46E5] text-white font-semibold rounded-lg transition-all duration-150 hover:from-[#5B5FE7] hover:to-[#4338CA] active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <LogIn size={18} />
                  Sign In
                </>
              )}
            </button>

            <div className="text-center">
              <p className="text-sm text-[#6F6F6F] dark:text-[#AAAAAA]">
                Don't have an account?{" "}
                <a
                  href={`/account/signup${typeof window !== "undefined" ? window.location.search : ""}`}
                  className="text-[#6366F1] hover:text-[#4F46E5] font-medium transition-colors"
                >
                  Sign up
                </a>
              </p>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}