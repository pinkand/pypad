<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch, computed } from 'vue'
import { useKnowledgeStore } from '@/stores/knowledge'
import { useAppStore } from '@/stores/app'
import { MASTERY_THRESHOLDS, KNOWLEDGE_DOMAINS } from '@/utils/constants'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { CSS2DRenderer, CSS2DObject } from 'three/examples/jsm/renderers/CSS2DRenderer.js'
import type { KnowledgeNode } from '@/types/knowledge'

const knowledgeStore = useKnowledgeStore()
const appStore = useAppStore()

const containerRef = ref<HTMLDivElement>()
const canvasRef = ref<HTMLCanvasElement>()
const cssContainerRef = ref<HTMLDivElement>()

let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let cssRenderer: CSS2DRenderer
let controls: OrbitControls
let animationId: number

// Particle System Variables
let particles: THREE.Points
let particleGeometry: THREE.BufferGeometry
let particleVelocities!: Float32Array
let particleOriginalPos!: Float32Array
const PARTICLE_COUNT = 1500
const mouse3D = new THREE.Vector3(0, 0, 0)
const targetAggregationPos = new THREE.Vector3(0, 0, 0)
let isAggregating = false
let aggregationTimer = 0

// Raycaster for mouse tracking
const raycaster = new THREE.Raycaster()
const mouse = new THREE.Vector2()
const plane = new THREE.Plane(new THREE.Vector3(0, 0, 1), 0) // Z=0 plane

// State for expanding/collapsing nodes
const expandedNodes = ref<Set<string>>(new Set(['python-core']))

const getStatusColor = (mastery: number) => {
  if (mastery >= MASTERY_THRESHOLDS.excellent) return 'var(--status-mastered)'
  if (mastery >= MASTERY_THRESHOLDS.good) return 'var(--status-learning)'
  if (mastery >= MASTERY_THRESHOLDS.weak) return 'var(--status-weak)'
  return 'var(--status-unlearned)'
}

const getStatusText = (mastery: number) => {
  if (mastery >= MASTERY_THRESHOLDS.excellent) return '已掌握'
  if (mastery >= MASTERY_THRESHOLDS.good) return '学习中'
  if (mastery >= MASTERY_THRESHOLDS.weak) return '薄弱'
  return '未学习'
}

// Generate soft circular texture for particles programmatically
const createParticleTexture = () => {
  const canvas = document.createElement('canvas')
  canvas.width = 64
  canvas.height = 64
  const ctx = canvas.getContext('2d')
  if (ctx) {
    const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32)
    gradient.addColorStop(0, 'rgba(255, 255, 255, 1)')
    gradient.addColorStop(0.3, 'rgba(255, 255, 255, 0.5)')
    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, 64, 64)
  }
  const texture = new THREE.CanvasTexture(canvas)
  return texture
}

const initParticleSystem = () => {
  particleGeometry = new THREE.BufferGeometry()
  const positions = new Float32Array(PARTICLE_COUNT * 3)
  particleVelocities = new Float32Array(PARTICLE_COUNT * 3)
  particleOriginalPos = new Float32Array(PARTICLE_COUNT * 3)

  for (let i = 0; i < PARTICLE_COUNT * 3; i += 3) {
    // Distribute particles in a large cylindrical/spherical volume
    const radius = 200 + Math.random() * 400
    const theta = Math.random() * Math.PI * 2
    const y = (Math.random() - 0.5) * 400

    const x = Math.cos(theta) * radius
    const z = Math.sin(theta) * radius

    positions[i] = x
    positions[i + 1] = y
    positions[i + 2] = z

    particleOriginalPos[i] = x
    particleOriginalPos[i + 1] = y
    particleOriginalPos[i + 2] = z

    particleVelocities[i] = (Math.random() - 0.5) * 0.2
    particleVelocities[i + 1] = (Math.random() - 0.5) * 0.2
    particleVelocities[i + 2] = (Math.random() - 0.5) * 0.2
  }

  particleGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))

  const material = new THREE.PointsMaterial({
    size: 4,
    map: createParticleTexture(),
    transparent: true,
    opacity: 0.6,
    color: 0x64748b, // Slate 500 (darker slate) for visibility on white background
    depthWrite: false,
    blending: THREE.NormalBlending
  })

  particles = new THREE.Points(particleGeometry, material)
  scene.add(particles)
}

const initScene = () => {
  if (!canvasRef.value || !containerRef.value || !cssContainerRef.value) return

  // Scene
  scene = new THREE.Scene()
  scene.background = new THREE.Color('#fafafa') // Light Apple background

  // Camera
  const aspect = containerRef.value.clientWidth / containerRef.value.clientHeight
  camera = new THREE.PerspectiveCamera(50, aspect, 0.1, 2000)
  camera.position.set(0, 80, 400) // Pulled back slightly for minimalist feel
  camera.lookAt(0, 20, 0)

  // WebGL Renderer for lines
  renderer = new THREE.WebGLRenderer({
    canvas: canvasRef.value,
    antialias: true,
    alpha: false,
    powerPreference: "high-performance"
  })
  renderer.setSize(containerRef.value.clientWidth, containerRef.value.clientHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))

  // CSS2D Renderer for HTML Cards
  cssRenderer = new CSS2DRenderer()
  cssRenderer.setSize(containerRef.value.clientWidth, containerRef.value.clientHeight)
  cssRenderer.domElement.style.position = 'absolute'
  cssRenderer.domElement.style.top = '0px'
  cssRenderer.domElement.style.left = '0px'
  cssRenderer.domElement.style.pointerEvents = 'none' 
  cssContainerRef.value.appendChild(cssRenderer.domElement)

  // Controls
  controls = new OrbitControls(camera, cssRenderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.autoRotate = false // Disable auto rotate for better mouse gravity interaction
  controls.maxDistance = 800
  controls.minDistance = 50
  controls.target.set(0, 30, 0)

  // Lighting
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.9)
  scene.add(ambientLight)
  
  const dirLight1 = new THREE.DirectionalLight(0xffffff, 0.5)
  dirLight1.position.set(50, 100, 50)
  scene.add(dirLight1)

  // Init Particles
  initParticleSystem()

  // Initial draw
  if (knowledgeStore.nodes.length > 0) {
    createKnowledgeNetwork()
  }

  // Watch for data updates to redraw
  watch(() => knowledgeStore.treeNodes, () => {
    createKnowledgeNetwork()
  }, { deep: true })
  
  // Watch mastery changes to update card UI without full redraw
  watch(() => knowledgeStore.masteryMap, () => {
    updateCards()
  }, { deep: true })

  // Mouse Move listener
  window.addEventListener('mousemove', onMouseMove)

  animate()
}

const onMouseMove = (event: MouseEvent) => {
  if (!containerRef.value) return
  const rect = containerRef.value.getBoundingClientRect()
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1

  raycaster.setFromCamera(mouse, camera)
  raycaster.ray.intersectPlane(plane, mouse3D)
}

// Store references to update DOM without recreating
const cardElements = new Map<string, HTMLElement>()
let currentLines: THREE.Object3D[] = []

const createKnowledgeNetwork = () => {
  // Clear only graph elements (lines, cards), keep particles and lights
  currentLines.forEach(line => {
    if ((line as any).geometry) (line as any).geometry.dispose()
    if ((line as any).material) (line as any).material.dispose()
    scene.remove(line)
  })
  currentLines = []
  
  // Clear old CSS2D objects
  scene.children.forEach(child => {
    if (child instanceof CSS2DObject) {
      scene.remove(child)
    }
  })
  cardElements.clear()
  
  const nodePositions = new Map<string, THREE.Vector3>()
  const parentChildEdges: Array<{source: string, target: string}> = []

  // Recursive layout function
  const layoutTree = (
    node: KnowledgeNode, 
    parentPos: THREE.Vector3, 
    level: number, 
    index: number, 
    siblingsCount: number, 
    spreadRadius: number, 
    currentAngle: number,
    arcAngle: number
  ) => {
    // Generous whitespace spacing
    const y = -20 + level * 60 
    
    let x = parentPos.x
    let z = parentPos.z
    
    let myAngle = currentAngle
    
    if (level > 0) {
       const angleStep = siblingsCount > 1 ? arcAngle / (siblingsCount - 1) : 0
       myAngle = currentAngle - arcAngle/2 + index * angleStep
       x += Math.cos(myAngle) * spreadRadius
       z += Math.sin(myAngle) * spreadRadius
    }
    
    // Add subtle noise to prevent perfect geometric shapes
    const noise = () => (Math.random() - 0.5) * (level === 0 ? 0 : 15.0)
    const pos = new THREE.Vector3(x + noise(), y + noise(), z + noise())
    nodePositions.set(node.id, pos)
    
    if (node.parentId) {
      parentChildEdges.push({ source: node.parentId, target: node.id })
    }
    
    // Check expansion state before rendering children
    if (node.children && node.children.length > 0 && expandedNodes.value.has(node.id)) {
      const childSpreadRadius = spreadRadius * (level === 0 ? 1.5 : 0.8)
      const childArcAngle = arcAngle * (level === 0 ? 1.0 : 0.7)
      node.children.forEach((child, i) => {
         layoutTree(child, pos, level + 1, i, node.children!.length, childSpreadRadius, myAngle, childArcAngle)
      })
    }
  }

  // Layout roots
  const roots = knowledgeStore.treeNodes
  if (roots.length > 0) {
    roots.forEach((root, i) => {
      const angle = (i / roots.length) * Math.PI * 2
      // Increased base spread radius for minimalist feel
      layoutTree(root, new THREE.Vector3(0,0,0), 0, i, roots.length, 120, angle, Math.PI * 2)
    })
  }

  // 1. Create Branches (Soft minimal lines)
  const lineMat = new THREE.LineBasicMaterial({
    color: 0xcfd4da, // Very soft blue-gray
    transparent: true,
    opacity: 0.4,
    linewidth: 1
  })
  
  parentChildEdges.forEach(edge => {
    const p1 = nodePositions.get(edge.source)
    const p2 = nodePositions.get(edge.target)
    if (p1 && p2) {
      // Use CatmullRomCurve3 for curved soft lines
      const distance = p1.distanceTo(p2)
      const midPoint = p1.clone().lerp(p2, 0.5)
      // Bow the line slightly based on distance to make it look organic
      midPoint.y -= distance * 0.1 
      midPoint.x += (Math.random() - 0.5) * distance * 0.1
      
      const curve = new THREE.CatmullRomCurve3([p1, midPoint, p2])
      const points = curve.getPoints(20)
      const geo = new THREE.BufferGeometry().setFromPoints(points)
      
      const line = new THREE.Line(geo, lineMat)
      scene.add(line)
      currentLines.push(line)
    }
  })

  // 3. Create Nodes (HTML Cards)
  knowledgeStore.nodes.forEach(node => {
    const pos = nodePositions.get(node.id)
    if (!pos) return // Skip nodes that aren't laid out (collapsed)
    
    const mastery = knowledgeStore.getNodeMastery(node.id) || 0
    const color = getStatusColor(mastery)
    const status = getStatusText(mastery)
    const isRoot = !node.parentId
    const hasChildren = node.children && node.children.length > 0
    const isExpanded = expandedNodes.value.has(node.id)
    
    // Create HTML element
    const div = document.createElement('div')
    div.className = `node-card ${isRoot ? 'node-root' : ''}`
    div.style.pointerEvents = 'auto' 
    
    // Toggle expand/collapse & trigger particle aggregation on click
    div.onclick = (e) => {
      e.stopPropagation()
      if (hasChildren) {
        if (isExpanded) {
          expandedNodes.value.delete(node.id)
        } else {
          expandedNodes.value.add(node.id)
        }
        createKnowledgeNetwork() // Re-layout
      }
      
      // Trigger Particle aggregation
      targetAggregationPos.copy(pos)
      isAggregating = true
      aggregationTimer = 60 // frames to aggregate
      
      // Open info panel
      appStore.openPanel(node.id)
    }
    
    const indicator = hasChildren ? `<span class="expand-indicator">${isExpanded ? '−' : '+'}</span>` : ''

    div.innerHTML = `
      <div class="card-content">
        <div class="card-header">
          <span class="card-dot" style="background-color: ${color}"></span>
          <span class="card-title">${node.name}</span>
          ${indicator}
        </div>
        <div class="card-progress">
          <div class="progress-bar-bg">
            <div class="progress-bar-fill" style="width: ${mastery}%; background-color: ${color}"></div>
          </div>
          <span class="progress-text">${mastery}%</span>
        </div>
        <div class="card-footer" style="color: ${color}">
          ${status}
        </div>
      </div>
    `
    
    cardElements.set(node.id, div)
    
    const cssObject = new CSS2DObject(div)
    cssObject.position.copy(pos)
    scene.add(cssObject)
  })
}

// Function to update existing cards without full rebuild
const updateCards = () => {
  knowledgeStore.nodes.forEach(node => {
    const div = cardElements.get(node.id)
    if (!div) return
    
    const mastery = knowledgeStore.getNodeMastery(node.id) || 0
    const color = getStatusColor(mastery)
    const status = getStatusText(mastery)
    
    const dot = div.querySelector('.card-dot') as HTMLElement
    const fill = div.querySelector('.progress-bar-fill') as HTMLElement
    const text = div.querySelector('.progress-text') as HTMLElement
    const footer = div.querySelector('.card-footer') as HTMLElement
    
    if (dot) dot.style.backgroundColor = color
    if (fill) {
      fill.style.width = `${mastery}%`
      fill.style.backgroundColor = color
    }
    if (text) text.innerText = `${mastery}%`
    if (footer) {
      footer.innerText = status
      footer.style.color = color
    }
  })
}

const updateParticles = () => {
  if (!particles) return
  
  const positions = particleGeometry.attributes.position!.array as Float32Array
  
  if (isAggregating && aggregationTimer > 0) {
    aggregationTimer--
  } else {
    isAggregating = false
  }

  for (let i = 0; i < PARTICLE_COUNT * 3; i += 3) {
    // Base drift
    positions[i]! += particleVelocities[i]!
    positions[i + 1]! += particleVelocities[i + 1]!
    positions[i + 2]! += particleVelocities[i + 2]!

    const pX = positions[i]!
    const pY = positions[i + 1]!
    const pZ = positions[i + 2]!

    // Distance to original pos - gentle pull back to maintain volume
    const dxO = particleOriginalPos[i]! - pX
    const dyO = particleOriginalPos[i + 1]! - pY
    const dzO = particleOriginalPos[i + 2]! - pZ
    
    particleVelocities[i]! += dxO * 0.0001
    particleVelocities[i + 1]! += dyO * 0.0001
    particleVelocities[i + 2]! += dzO * 0.0001

    // Apply mouse gravity (knowledge flow)
    if (mouse3D && !isAggregating) {
      const dxM = mouse3D.x - pX
      const dyM = mouse3D.y - pY
      const dzM = mouse3D.z - pZ
      const distSq = dxM * dxM + dyM * dyM + dzM * dzM
      
      // Pull particles within range
      if (distSq < 20000) {
        const force = 0.05 / Math.sqrt(distSq)
        particleVelocities[i]! += dxM * force
        particleVelocities[i + 1]! += dyM * force
        particleVelocities[i + 2]! += dzM * force
      }
    }

    // Apply Click Aggregation Gravity
    if (isAggregating) {
      const dxA = targetAggregationPos.x - pX
      const dyA = targetAggregationPos.y - pY
      const dzA = targetAggregationPos.z - pZ
      const distSqA = dxA * dxA + dyA * dyA + dzA * dzA
      
      // Pull particles strongly towards target
      if (distSqA > 10) {
        const force = 0.2 / Math.sqrt(distSqA)
        particleVelocities[i]! += dxA * force
        particleVelocities[i + 1]! += dyA * force
        particleVelocities[i + 2]! += dzA * force
      }
    }

    // Dampen velocity to prevent chaos
    particleVelocities[i]! *= 0.98
    particleVelocities[i + 1]! *= 0.98
    particleVelocities[i + 2]! *= 0.98
  }

  particleGeometry.attributes.position!.needsUpdate = true
}

const animate = () => {
  animationId = requestAnimationFrame(animate)
  controls.update()
  updateParticles()
  
  renderer.render(scene, camera)
  cssRenderer.render(scene, camera)
}

const handleResize = () => {
  if (!containerRef.value) return
  camera.aspect = containerRef.value.clientWidth / containerRef.value.clientHeight
  camera.updateProjectionMatrix()
  renderer.setSize(containerRef.value.clientWidth, containerRef.value.clientHeight)
  cssRenderer.setSize(containerRef.value.clientWidth, containerRef.value.clientHeight)
}

onMounted(() => {
  initScene()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  cancelAnimationFrame(animationId)
  window.removeEventListener('resize', handleResize)
  window.removeEventListener('mousemove', onMouseMove)
  renderer.dispose()
})
</script>

<template>
  <div ref="containerRef" class="universe-container">
    <canvas ref="canvasRef" class="universe-canvas" />
    <div ref="cssContainerRef" class="css-container" />
    
    <!-- Minimalist Title -->
    <div class="universe-title">
      <h1>Python Learning OS</h1>
      <p>知识流动系统</p>
    </div>
  </div>
</template>

<style scoped>
.universe-container {
  width: 100vw;
  height: 100vh;
  position: absolute;
  top: 0;
  left: 0;
  overflow: hidden;
  background: transparent;
}

.universe-canvas, .css-container {
  width: 100%;
  height: 100%;
  display: block;
  position: absolute;
  top: 0;
  left: 0;
}

/* 
  Styles for the dynamically generated CSS2D objects.
*/
:deep(.node-card) {
  width: 170px;
  cursor: pointer;
  user-select: none;
}

:deep(.card-content) {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: 16px;
  padding: 14px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.03);
  transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.3s, background 0.3s;
  transform: scale(0.9);
}

:deep(.node-root .card-content) {
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(0, 0, 0, 0.1);
  transform: scale(1.1);
}

:deep(.node-card:hover .card-content) {
  background: rgba(255, 255, 255, 0.95);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
  transform: translateY(-4px) scale(0.95);
}

:deep(.node-card.node-root:hover .card-content) {
  transform: translateY(-4px) scale(1.15);
}

:deep(.node-card:hover) {
  z-index: 10;
}

:deep(.card-header) {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

:deep(.card-dot) {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
  box-shadow: 0 0 8px currentColor; /* Subtle bloom */
}

:deep(.card-title) {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
}

:deep(.expand-indicator) {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 300;
  padding: 0 4px;
}

:deep(.card-progress) {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

:deep(.progress-bar-bg) {
  flex: 1;
  height: 4px;
  background-color: var(--bg-tertiary);
  border-radius: 2px;
  overflow: hidden;
}

:deep(.progress-bar-fill) {
  height: 100%;
  border-radius: 2px;
  transition: width 0.5s cubic-bezier(0.4, 0, 0.2, 1);
}

:deep(.progress-text) {
  font-size: 11px;
  font-family: var(--font-mono);
  color: var(--text-secondary);
  width: 26px;
  text-align: right;
}

:deep(.card-footer) {
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.universe-title {
  position: absolute;
  top: 40px;
  left: 40px;
  z-index: 5;
  pointer-events: none;
}

.universe-title h1 {
  font-size: 28px;
  font-weight: 800;
  letter-spacing: -1px;
  color: var(--text-primary);
  margin-bottom: 8px;
  font-family: var(--font-sans);
}

.universe-title p {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
  letter-spacing: 0.5px;
}
</style>