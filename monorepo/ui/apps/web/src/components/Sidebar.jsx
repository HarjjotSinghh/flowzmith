import { useState } from "react";
import {
  LayoutDashboard,
  Code,
  Layers,
  Rocket,
  TestTube,
  Settings,
  ChevronDown,
  MessageCircle,
} from "lucide-react";

export default function Sidebar({ onClose }) {
  const [activeItem, setActiveItem] = useState("Dashboard");
  const [expandedMenus, setExpandedMenus] = useState({});

  const toggleSubmenu = (item) => {
    setExpandedMenus((prev) => ({
      ...prev,
      [item]: !prev[item],
    }));
  };

  const handleItemClick = (itemName, hasSubmenu) => {
    setActiveItem(itemName);
    if (hasSubmenu) {
      toggleSubmenu(itemName);
    }
    // Close sidebar on mobile when item is clicked
    if (onClose && typeof window !== "undefined" && window.innerWidth < 1024) {
      onClose();
    }
  };

  const navigationItems = [
    { name: "Dashboard", icon: LayoutDashboard, hasSubmenu: false, href: "/" },
    { name: "Contracts", icon: Code, hasSubmenu: false, href: "/contracts" },
    {
      name: "Components",
      icon: Layers,
      hasSubmenu: false,
      href: "/components",
    },
    { name: "Deploy", icon: Rocket, hasSubmenu: false, href: "/deploy" },
    { name: "Testing", icon: TestTube, hasSubmenu: false, href: "/testing" },
    { name: "Settings", icon: Settings, hasSubmenu: false, href: "/settings" },
  ];

  return (
    <div className="w-60 bg-[#F3F3F3] dark:bg-[#1A1A1A] flex-shrink-0 flex flex-col h-full">
      {/* Brand Logo */}
      <div className="p-4 flex justify-start">
        <div className="w-12 h-12 bg-white dark:bg-[#262626] rounded-full border border-[#E4E4E4] dark:border-[#404040] flex items-center justify-center">
          {/* Web3 Brand mark */}
          <div className="w-8 h-8 bg-gradient-to-br from-[#6366F1] to-[#8B5CF6] rounded-full flex items-center justify-center">
            <Code size={16} className="text-white" />
          </div>
        </div>
      </div>

      {/* Navigation Menu */}
      <nav className="flex-1 px-4">
        <div className="space-y-2">
          {navigationItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeItem === item.name;
            const isExpanded = expandedMenus[item.name];

            return (
              <div key={item.name}>
                <a
                  href={item.href}
                  onClick={() => handleItemClick(item.name, item.hasSubmenu)}
                  className={`w-full flex items-center justify-between px-3 py-3 rounded-lg transition-all duration-200 block ${
                    isActive
                      ? "bg-white dark:bg-[#262626] border border-[#E4E4E4] dark:border-[#404040] text-black dark:text-white"
                      : "text-black/70 dark:text-white/70 hover:text-black dark:hover:text-white hover:bg-white/50 dark:hover:bg-white/10 active:bg-white/70 dark:active:bg-white/15 active:scale-[0.98]"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon
                      size={20}
                      className={
                        isActive
                          ? "text-black dark:text-white"
                          : "text-black/70 dark:text-white/70"
                      }
                    />
                    <span
                      className={`font-medium text-sm font-plus-jakarta ${
                        isActive
                          ? "text-black dark:text-white"
                          : "text-black/70 dark:text-white/70"
                      }`}
                    >
                      {item.name}
                    </span>
                  </div>
                  {item.hasSubmenu && (
                    <ChevronDown
                      size={16}
                      className={`transition-transform duration-200 ${
                        isExpanded ? "rotate-180" : ""
                      } ${isActive ? "text-black dark:text-white" : "text-black/70 dark:text-white/70"}`}
                    />
                  )}
                </a>
              </div>
            );
          })}
        </div>
      </nav>

      {/* Utility Actions */}
      <div className="p-4">
        {/* Chat Button */}
        <button className="w-10 h-10 bg-white dark:bg-[#262626] rounded-full border border-[#DADADA] dark:border-[#404040] flex items-center justify-center transition-all duration-200 hover:bg-[#F8F8F8] dark:hover:bg-[#2A2A2A] hover:border-[#C0C0C0] dark:hover:border-[#505050] active:bg-[#F0F0F0] dark:active:bg-[#333333] active:scale-95">
          <MessageCircle
            size={18}
            className="text-black/70 dark:text-white/70"
          />
        </button>
      </div>
    </div>
  );
}
