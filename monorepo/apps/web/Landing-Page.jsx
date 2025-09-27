// LandingPage.jsx - WITH PROPER TEXT ANIMATIONS
"use client";

import { useRef, useMemo, useState, useEffect } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { MeshDistortMaterial, Sphere, ScrollControls, Scroll, useScroll, useGLTF, Environment } from '@react-three/drei';
import HyperspeedWrapper from "./HyperSpeedWrapper";
import * as THREE from 'three';

// --- Enhanced Text Block Component with Proper Animations ---
const AnimatedTextBlock = ({ textData, currentTextIndex }) => {
  const textRefs = useRef([]);
  
  useEffect(() => {
    // Initialize refs array
    textRefs.current = textRefs.current.slice(0, textData.length);
  }, [textData.length]);

  useEffect(() => {
    // Animate text visibility based on currentTextIndex
    textRefs.current.forEach((ref, index) => {
      if (!ref) return;
      
      const item = textData[index];
      const config = item.config || {};
      
      if (index === currentTextIndex) {
        // Show current text
        ref.style.opacity = '1';
        
        // Use configured transform or default
        const showTransform = config.animation?.showTransform || 'translateY(0px) scale(1)';
        ref.style.transform = showTransform;
        
        // Enable pointer events if CTA is present
        ref.style.pointerEvents = item.cta ? 'auto' : 'none';
      } else {
        // Hide other texts
        ref.style.opacity = '0';
        
        // Use configured transform or default
        const hideTransform = config.animation?.hideTransform || 'translateY(20px) scale(0.95)';
        ref.style.transform = hideTransform;
        
        ref.style.pointerEvents = 'none';
      }
    });
  }, [currentTextIndex, textData]);

  // Helper function to generate style object from config
  const generateStyles = (styleConfig) => {
    if (!styleConfig) return {};
    
    const styles = {};
    Object.keys(styleConfig).forEach(key => {
      // Convert camelCase to kebab-case for CSS properties
      const cssKey = key.replace(/([A-Z])/g, '-$1').toLowerCase();
      styles[cssKey] = styleConfig[key];
    });
    return styles;
  };

  return (
    <>
      {textData.map((item, index) => {
        const config = item.config || {};
        const layout = config.layout || {};
        const animation = config.animation || {};
        
        // Container positioning
        const containerPosition = layout.position || 'center'; // center, top-left, top-right, bottom-left, bottom-right, custom
        const customPosition = layout.customPosition || {};
        
        // Get positioning classes and styles
        let positionClasses = '';
        let positionStyles = {};
        
        switch (containerPosition) {
          case 'top-left':
            positionClasses = 'fixed top-8 left-8';
            break;
          case 'top-right':
            positionClasses = 'fixed top-8 right-8';
            break;
          case 'bottom-left':
            positionClasses = 'fixed bottom-8 left-8';
            break;
          case 'bottom-right':
            positionClasses = 'fixed bottom-8 right-8';
            break;
          case 'top-center':
            positionClasses = 'fixed top-8 left-1/2 -translate-x-1/2';
            break;
          case 'bottom-center':
            positionClasses = 'fixed bottom-8 left-1/2 -translate-x-1/2';
            break;
          case 'center-left':
            positionClasses = 'fixed top-1/2 left-8 -translate-y-1/2';
            break;
          case 'center-right':
            positionClasses = 'fixed top-1/2 right-8 -translate-y-1/2';
            break;
          case 'custom':
            positionClasses = 'fixed';
            positionStyles = {
              top: customPosition.top || '50%',
              left: customPosition.left || '50%',
              right: customPosition.right || 'auto',
              bottom: customPosition.bottom || 'auto',
              transform: customPosition.transform || 'translate(-50%, -50%)'
            };
            break;
          default: // center
            positionClasses = 'fixed top-1/2 left-1/2';
            positionStyles = { transform: 'translate(-50%, -50%)' };
        }
        
        // Container styling
        const containerWidth = layout.containerWidth || 'w-[90vw] md:w-auto';
        const containerClasses = `${positionClasses} ${containerWidth} pointer-events-none z-50`;
        const containerAlignment = layout.alignment || 'text-center';
        
        // Animation configuration
        const transitionDuration = animation.duration || '0.8s';
        const transitionEasing = animation.easing || 'cubic-bezier(0.25, 0.46, 0.45, 0.94)';
        const hideTransform = animation.hideTransform || 'translateY(20px) scale(0.95)';
        
        return (
          <div
            key={index}
            ref={(el) => (textRefs.current[index] = el)}
            className={`${containerClasses} ${containerAlignment} pointer-events-none`}
            style={{
              opacity: 0,
              transform: hideTransform,
              transition: `all ${transitionDuration} ${transitionEasing}`,
              ...positionStyles,
              ...generateStyles(layout.containerStyles)
            }}
          >
            <div 
              className={layout.wrapperClasses || "max-w-4xl mx-auto"}
              style={generateStyles(layout.wrapperStyles)}
            >
              {/* Configurable Title */}
              {item.title && (
                <h1 
                  className={config.title?.classes || "text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight mb-4"}
                  style={generateStyles(config.title?.styles)}
                >
                  {item.title}
                </h1>
              )}
              
              {/* Configurable Subtitle */}
              {item.subtitle && (
                <p 
                  className={config.subtitle?.classes || "text-lg md:text-xl lg:text-2xl opacity-80 max-w-2xl mx-auto"}
                  style={generateStyles(config.subtitle?.styles)}
                >
                  {item.subtitle}
                </p>
              )}
              
              {/* Configurable Additional Content */}
              {item.content && (
                <div 
                  className={config.content?.classes || "mt-4"}
                  style={generateStyles(config.content?.styles)}
                >
                  {typeof item.content === 'string' ? (
                    <p>{item.content}</p>
                  ) : (
                    item.content
                  )}
                </div>
              )}
              
              {/* Configurable CTA Button(s) */}
              {item.cta && (
                <div 
                  className={config.cta?.wrapperClasses || "mt-8"}
                  style={generateStyles(config.cta?.wrapperStyles)}
                >
                  {Array.isArray(item.cta) ? (
                    // Multiple buttons
                    item.cta.map((button, btnIndex) => (
                      <button
                        key={btnIndex}
                        className={button.classes || config.cta?.classes || "px-10 py-4 bg-cyan-400 text-black font-bold rounded-lg text-xl pointer-events-auto hover:bg-cyan-300 transition-all duration-300 shadow-lg shadow-cyan-400/50 hover:scale-105 mr-4"}
                        style={generateStyles(button.styles || config.cta?.styles)}
                        onClick={button.onClick}
                      >
                        {button.text}
                      </button>
                    ))
                  ) : (
                    // Single button
                    <button
                      className={item.cta.classes || config.cta?.classes || "px-10 py-4 bg-cyan-400 text-black font-bold rounded-lg text-xl pointer-events-auto hover:bg-cyan-300 transition-all duration-300 shadow-lg shadow-cyan-400/50 hover:scale-105"}
                      style={generateStyles(item.cta.styles || config.cta?.styles)}
                      onClick={item.cta.onClick}
                    >
                      {item.cta.text || "Start Building Now"}
                    </button>
                  )}
                </div>
              )}
              
              {/* Custom Elements */}
              {item.customElements && item.customElements.map((element, elemIndex) => (
                <div
                  key={elemIndex}
                  className={element.classes}
                  style={generateStyles(element.styles)}
                >
                  {element.content}
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </>
  );
};

// --- Scroll Controller Component ---
const ScrollController = ({ onScrollUpdate, totalPages }) => {
  const scroll = useScroll();

  useFrame(() => {
    const offset = scroll.offset;
    onScrollUpdate(offset);
  });

  return null;
};

// --- Side Scroll Sphere Component ---
const SideScrollSphere = ({ positionZ, color, side, scale = 10, startScroll, endScroll }) => {
  const meshRef = useRef();
  const scroll = useScroll();

  const positionX = side === 'left' ? -4.2 : 4.2;
  const positionY = 1;

  useFrame((state, delta) => {
    const offset = scroll.offset;

    const scrollProgress = THREE.MathUtils.mapLinear(
      offset,
      startScroll,
      endScroll,
      0,
      1
    );

    const currentZ = THREE.MathUtils.mapLinear(scrollProgress, 0, 1, positionZ, positionZ + 50);
    meshRef.current.position.z = currentZ;

    meshRef.current.rotation.x += delta * 2;
    meshRef.current.rotation.y += delta * 1.5;

    let visibility = 1 - Math.abs(scrollProgress - 0.5) * 2;
    visibility = Math.max(0.75, Math.min(1.6, visibility));

    meshRef.current.scale.setScalar(scale * visibility);

    if (meshRef.current.material) {
      meshRef.current.material.opacity = visibility;
    }
  });

  return (
    <Sphere
      ref={meshRef}
      args={[1, 32, 32]}
      scale={scale}
      position={[positionX, positionY, positionZ]}
    >
      <MeshDistortMaterial
        color={color}
        speed={1}
        distort={0.4}
        wireframe={true}
        transparent={true}
        opacity={1}
      />
    </Sphere>
  );
};

// --- Starting Prop Component ---
const GLBStartingProp = ({ modelPath, FinalY, InitialY, InitialScale, finalScale }) => {
  const groupRef = useRef();
  const scroll = useScroll();
  const { scene } = useGLTF(modelPath);

  const model = useMemo(() => {
    const clone = scene.clone(true);
    return clone;
  }, [scene]);

  const initialScale = InitialScale || 6.5;
  const initialY = InitialY;
  const initialZ = -5;

  const shinyMaterial = useMemo(() => {
    return new THREE.MeshPhysicalMaterial({
      color: 0x00FFFF,
      metalness: 0.6,
      roughness: 0.1,
      clearcoat: 1.0,
      clearcoatRoughness: 0.1,
    });
  }, []);

  useFrame(() => {
    const offset = scroll.offset;
    const scrollProgress = Math.min(1, offset * 3);
    groupRef.current.position.y = initialY + scrollProgress * FinalY;
    groupRef.current.scale.setScalar(initialScale + scrollProgress * finalScale);
    groupRef.current.rotation.y += 0.01;

    model.traverse((child) => {
      if (child.isMesh) {
        child.material = shinyMaterial;
      }
    });
  });

  return (
    <group ref={groupRef} position={[0, initialY, initialZ]} scale={initialScale}>
      <primitive object={model} />
    </group>
  );
};

// --- Shiny Tile Component ---
const ShinyTile = ({ side, positionZ, yOffset, startScroll, endScroll, scale = [17, 3.3, 10] }) => {
  const groupRef = useRef();
  const scroll = useScroll();

  const positionX = side === 'left' ? -50 : 50;

  useFrame(() => {
    const offset = scroll.offset;
    const scrollProgress = THREE.MathUtils.mapLinear(offset, startScroll, endScroll, 0, 1);
    groupRef.current.position.z = THREE.MathUtils.mapLinear(scrollProgress, 0, 1, positionZ, positionZ + 50);
  });

  return (
    <group ref={groupRef} position={[positionX, yOffset, positionZ]}>
      <mesh scale={scale}>
        <boxGeometry args={[1, 1, 1]} />
        <meshPhysicalMaterial
          color="#0a2929"
          metalness={0.9}
          roughness={0.2}
          transparent={true}
        />
      </mesh>
      <mesh scale={[scale[0] * 1.001, scale[1] * 0.25, scale[2] * 1.001]}>
        <boxGeometry args={[1, 1, 1]} />
        <meshStandardMaterial
          color="#008080"
          emissive="#008080"
          emissiveIntensity={3}
          toneMapped={false}
          transparent={true}
        />
      </mesh>
    </group>
  );
};

// Lighting Component
const Lights = () => (
  <>
    <ambientLight intensity={0.5} />
    <pointLight position={[0, 0, 5]} intensity={10} color={'#FFFFFF'} />
    <pointLight position={[0, -5, -5]} intensity={2} color={'#FFAA00'} />
  </>
);

// --- Main Landing Page Component ---
export default function LandingPage() {
  const [currentTextIndex, setCurrentTextIndex] = useState(0);
  const totalPages = 8;
  const sphereScrollRange = 0.2;
  const gapBetweenSpheres = 0.03;
  const tileScrollRange = 0.15;

  // Configuration for the side spheres
  const sphereItems = [
    { z: -30, color: 'hotpink', scale: 2.0, side: 'left', startScroll: 0.15, endScroll: 0.15 + sphereScrollRange },
    { z: -30, color: 'cyan', scale: 2.2, side: 'right', startScroll: 0.15 + sphereScrollRange + gapBetweenSpheres, endScroll: 0.15 + sphereScrollRange + gapBetweenSpheres + sphereScrollRange },
    { z: -30, color: 'lime', scale: 2.5, side: 'left', startScroll: 0.15 + (sphereScrollRange + gapBetweenSpheres) * 2, endScroll: 0.15 + (sphereScrollRange + gapBetweenSpheres) * 2 + sphereScrollRange },
    // { z: -30, color: 'yellow', scale: 2.0, side: 'right', startScroll: 0.15 + (sphereScrollRange + gapBetweenSpheres) * 3, endScroll: 0.15 + (sphereScrollRange + gapBetweenSpheres) * 3 + sphereScrollRange },
  ];

  // Configuration for the shiny tiles
  const tileItems = [
    { z: -10, side: 'left', yOffset: -10, startScroll: 0.1, endScroll: 0.1 + tileScrollRange },
    { z: -15, side: 'right', yOffset: 20, startScroll: 0.1, endScroll: 0.1 + tileScrollRange },
    { z: -25, side: 'right', yOffset: 20, startScroll: 0.25, endScroll: 0.25 + tileScrollRange },
    { z: -40, side: 'left', yOffset: -10, startScroll: 0.3, endScroll: 0.3 + tileScrollRange },
    { z: -35, side: 'left', yOffset: 20, startScroll: 0.5, endScroll: 0.5 + tileScrollRange },
    { z: -45, side: 'right', yOffset: -10, startScroll: 0.7, endScroll: 0.7 + tileScrollRange },
    // { z: -50, side: 'left', yOffset: 20, startScroll: 0.9, endScroll: 0.9 + tileScrollRange },
    { z: -30, side: 'left', yOffset: 20, startScroll: 0.4, endScroll: 0.4 + tileScrollRange },
    { z: -30, side: 'right', yOffset: -10, startScroll: 0.4, endScroll: 0.4 + tileScrollRange },
    { z: -42, side: 'right', yOffset: 20, startScroll: 0.6, endScroll: 0.6 + tileScrollRange },
    { z: -42, side: 'left', yOffset: -10, startScroll: 0.6, endScroll: 0.6 + tileScrollRange },
  ];

  // Text content with proper timing
const textData = [
    {
      title: "Flowzmith",
      subtitle: "AI-Powered Smart Contracts for Flow.",
      scrollRange: { start: 0, end: 0.12 },
      config: {
        layout: {
          position: 'bottom-left', // center, top-left, top-right, bottom-left, bottom-right, top-center, bottom-center, center-left, center-right, custom
          alignment: 'text-start',
          containerWidth: 'w-[90vw] md:w-auto mx-[15vw] mb-[7vh]',
          wrapperClasses: 'max-w-4xl mx-auto text-start',
        },
        title: {
          classes: 'text-4xl md:text-6xl lg:text-7xl font-black font-mono tracking-tight mb-4 text-white border-b-2 border-white/80 pb-2 min-w-[70vw]',
        },
        subtitle: {
          classes: 'text-lg text-start md:text-xl lg:text-2xl opacity-90 w-full mx-auto text-white ',
        },
        animation: {
          duration: '0.8s',
          easing: 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
          hideTransform: 'translateY(20px) scale(0.95)',
          showTransform: 'translateY(0px) scale(1)'
        }
      }
    },
    {
      title: "Overcoming LLM Uncertainty",
      subtitle: "Our context-rich, fine-tuned models understand blockchain-specific patterns, ensuring your contracts are not just syntactically correct, but functionally secure.",
      scrollRange: { start: 0.12, end: 0.35 },
      config: {
        layout: {
          position: 'bottom-right',
          alignment: 'text-end',
          containerWidth: 'w-[70vw] mb-[4vh]',
          wrapperClasses: 'max-w-4xl mx-auto text-end',
        },
        title: {
          classes: 'text-6xl font-black font-mono tracking-tight mb-4 text-white border-b-2 border-white/80 pb-2 min-w-[60vw]',
        },
        subtitle: {
          classes: 'text-xl opacity-90 w-full text-white leading-relaxed text-center min-w-[60vw]',
        },
        animation: {
          duration: '1s',
          hideTransform: 'translateX(-30px) scale(0.9) rotateY(15deg)',
          showTransform: 'translateX(0px) scale(1) rotateY(0deg)'
        }
      }
    },
    {
      title: "Seamlessly Deploy with Confidence",
      subtitle: "Integrate with the Flow SDK for automated deployment to testnet and mainnet, complete with real-time transaction monitoring.",
      content: "✓ Automated Testing     ✓ Real-time Monitoring     ✓ Version Control",
      scrollRange: { start: 0.35, end: 0.58 },
      config: {
        layout: {
          position: 'custom',
          customPosition: {
            top: '60%',
            left: '10%',
            transform: 'translate(-50%, -50%)'
          },
          alignment: 'text-left',
          wrapperClasses: 'max-w-5xl mx-auto p-8 text-start',
        },
        title: {
          classes: 'text-5xl font-black font-mono tracking-tight mb-4 text-white border-b-2 border-white/80 pb-2 min-w-[60vw]',
        },
        subtitle: {
          classes: 'text-xl opacity-90 w-full text-white leading-relaxed text-start min-w-[60vw] ',
        },
        content: {
          classes: 'text-white font-semibold font-mono text-xl mt-6 flex flex-col md:flex-row md:space-x-6 space-y-2 md:space-y-0',
        },
        animation: {
          duration: '1.2s',
          hideTransform: 'translateY(40px) scale(0.85) rotateX(10deg)',
          showTransform: 'translateY(0px) scale(1) rotateX(0deg)'
        }
      }
    },
    {
      title: "From NFTs to DeFi",
      subtitle: "Build anything from NFT marketplaces and DeFi protocols to complex gaming economies and enterprise solutions with our versatile platform.",
      scrollRange: { start: 0.58, end: 0.81 },
      config: {
        layout: {
          position: 'bottom-right',
          alignment: 'text-end',
          containerWidth: 'w-[70vw] mb-[4vh]',
          wrapperClasses: 'max-w-4xl mx-auto text-center',
        },
        title: {
          classes: 'text-6xl font-black font-mono tracking-tight mb-4 text-white border-b-2 border-white/80 pb-2 min-w-[20vw]',
        },
        subtitle: {
          classes: 'text-xl opacity-90 w-full text-white leading-relaxed text-center min-w-[20vw]',
        },
        animation: {
          duration: '0.6s',
          easing: 'cubic-bezier(0.34, 1.56, 0.64, 1)',
          hideTransform: 'scale(0.8) rotateZ(-5deg)',
          showTransform: 'scale(1) rotateZ(0deg)'
        }
      }
    },
    {
      title: "Join the Future of Smart Contract Development",
      subtitle: "Stop wrestling with boilerplate. Start building with intelligence.",
      cta: [
        {
          text: "Start Building Now",
          classes: "px-8 py-4 bg-gradient-to-r from-cyan-500 to-teal-600 text-white font-bold rounded-lg text-lg pointer-events-auto hover:from-cyan-400 hover:to-teal-500 transition-all duration-300 shadow-lg hover:scale-105 mr-4",
          onClick: () => console.log("Start Building clicked")
        },
      ],
      scrollRange: { start: 0.81, end: 1 },
      customElements: [
        {
          classes: 'mt-[5vh] flex justify-center items-center space-x-4 text-md text-white',
          content: (
            <>
              <span>🚀 Free to start</span>
              <span>•</span>
              <span>⚡ Deploy in seconds</span>
              <span>•</span>
              <span>🔒 Enterprise ready</span>
            </>
          )
        }
      ],
      config: {
        layout: {
          position: 'custom',
          customPosition: {
            top: '25%',
            left: '18%',
            transform: 'translate(-50%, -50%)'
          },
          alignment: 'text-center',
          wrapperClasses: 'max-w-5xl mx-auto pointer-events-none select-none user-select-none ',
          
        },
        title: {
          classes: 'text-3xl md:text-5xl lg:text-6xl font-bold tracking-tight mb-6 text-white font-mono border-b-2 border-white/80 pb-2 min-w-[50vw]',
        },
        subtitle: {
          classes: 'text-xl md:text-2xl lg:text-3xl opacity-90 max-w-3xl mx-auto text-white mb-8 leading-relaxed',
        },
        cta: {
          wrapperClasses: 'mt-8 flex flex-col md:flex-row justify-center items-center gap-4',
        },
        animation: {
          duration: '1s',
          easing: 'cubic-bezier(0.23, 1, 0.32, 1)',
          hideTransform: 'translateY(50px) scale(0.9) rotateX(20deg)',
          showTransform: 'translateY(0px) scale(1) rotateX(0deg)'
        }
      }
    }
  ];

  // Handle scroll updates and determine current text
  const handleScrollUpdate = (scrollOffset) => {
    // Determine which text should be shown based on scroll position
    for (let i = 0; i < textData.length; i++) {
      const { start, end } = textData[i].scrollRange;
      if (scrollOffset >= start && scrollOffset < end) {
        if (currentTextIndex !== i) {
          setCurrentTextIndex(i);
        }
        break;
      }
    }
  };

  return (
    <div className="relative w-full min-h-screen bg-black overflow-hidden">
      {/* Hyperspeed Background */}
      <div className="fixed top-0 left-0 w-full h-full z-0">
        <HyperspeedWrapper />
      </div>

      {/* Header */}
      <div className='w-full h-[15vh] flex items-center justify-between px-[13vw] fixed top-0 left-0 z-[999]'>
        <div>
          <h1 className='text-white font-black font-mono text-4xl'>Flowzmith</h1>
        </div>
        <button className='px-8 py-4 bg-gradient-to-r from-cyan-500 to-teal-600 text-white font-bold rounded-lg text-lg pointer-events-auto hover:from-cyan-400 hover:to-teal-500 transition-all duration-300 shadow-lg hover:scale-105 mr-4'>
          Start Building Now
        </button>
      </div>

      {/* 3D Scene */}
      <div className="fixed top-0 left-0 w-full h-full z-10">
        <Canvas
          className="pointer-events-none"
          camera={{ fov: 80, near: 0.5, far: 1000, position: [0, 0, 10] }}
        >
          <ScrollControls pages={totalPages} damping={0.13}>
            <Environment preset="city" />
            <Lights />

            {/* Scroll Controller */}
            <ScrollController onScrollUpdate={handleScrollUpdate} totalPages={totalPages} />

            {/* The Starting Prop */}
            <GLBStartingProp 
              modelPath={'/PipeJoint1.glb'} 
              FinalY={50} 
              InitialY={2} 
              finalScale={1} 
              InitialScale={11.4} 
            />

            {/* Side-scrolling spheres */}
            {sphereItems.map((item, index) => (
              <SideScrollSphere
                key={`sphere-${index}`}
                positionZ={item.z}
                color={item.color}
                scale={item.scale}
                side={item.side}
                startScroll={item.startScroll}
                endScroll={item.endScroll}
              />
            ))}

            {/* Shiny tiles */}
            {tileItems.map((item, index) => (
              <ShinyTile
                key={`tile-${index}`}
                positionZ={item.z}
                side={item.side}
                yOffset={item.yOffset}
                startScroll={item.startScroll}
                endScroll={item.endScroll}
              />
            ))}
          </ScrollControls>
        </Canvas>
      </div>

      {/* Animated Text Overlay */}
      <AnimatedTextBlock textData={textData} currentTextIndex={currentTextIndex} />

      {/* Scroll trigger (invisible) */}
      <div className="absolute top-0 left-0 w-full h-[700vh] overflow-y-scroll pointer-events-auto opacity-0" />

      {/* Background Effects */}
      <div className="fixed -top-14 left-0 w-[40vw] h-[12vh] bg-[teal] blur-[100px] rounded-full"></div>
      <div className="fixed top-0 -left-40 w-[29vw] h-[32vh] bg-[teal] blur-[200px] rounded-full"></div>
      <div className="fixed -top-14 right-0 w-[40vw] h-[12vh] bg-[teal] blur-[100px] rounded-full"></div>
      <div className="fixed top-0 -right-40 w-[29vw] h-[32vh] bg-[teal] blur-[200px] rounded-full"></div>
      <div className="fixed -top-20 left-1/2 -translate-x-1/2 w-[40vw] h-[12vh] bg-[teal] blur-[100px] rounded-full"></div>
      <div className="fixed -top-20 left-0 w-screen h-[10vh] bg-[cyan] blur-[250px] rounded-full"></div>
    </div>
  );
}
