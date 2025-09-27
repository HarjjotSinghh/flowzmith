import { useEffect } from "react";
import { Code, LogOut } from "lucide-react";
import useAuth from "@/utils/useAuth";

export default function Logout() {
  const { signOut } = useAuth();

  useEffect(() => {
    // Auto-logout when page loads
    const handleSignOut = async () => {
      await signOut({
        callbackUrl: "/",
        redirect: true,
      });
    };
    
    handleSignOut();
  }, [signOut]);

  const handleManualSignOut = async () => {
    await signOut({
      callbackUrl: "/",
      redirect: true,
    });
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
            Signing you out...
          </p>
        </div>

        {/* Sign Out Card */}
        <div className="bg-white dark:bg-[#1E1E1E] rounded-xl border border-[#E6E6E6] dark:border-[#333333] p-6 shadow-lg text-center">
          <LogOut size={48} className="mx-auto text-[#6366F1] mb-4" />
          
          <h2 className="text-xl font-semibold text-black dark:text-white mb-2">
            Sign Out
          </h2>
          
          <p className="text-[#6F6F6F] dark:text-[#AAAAAA] mb-6">
            You are being signed out of your account. This may take a moment.
          </p>

          <button
            onClick={handleManualSignOut}
            className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-b from-[#252525] to-[#0F0F0F] dark:from-[#FFFFFF] dark:to-[#E0E0E0] text-white dark:text-black font-semibold rounded-lg transition-all duration-150 hover:from-[#2d2d2d] hover:to-[#171717] dark:hover:from-[#F0F0F0] dark:hover:to-[#D0D0D0] active:scale-95"
          >
            <LogOut size={18} />
            Sign Out Now
          </button>

          <div className="mt-4">
            <a
              href="/"
              className="text-[#6366F1] hover:text-[#4F46E5] font-medium transition-colors"
            >
              Return to Dashboard
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}