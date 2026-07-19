<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch, computed } from 'vue'
import { useKnowledgeStore } from '@/stores/knowledge'
import { useAppStore } from '@/stores/app'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { NODE_CATEGORIES } from '@/utils/constants'

const knowledgeStore = useKnowledgeStore()
const appStore = useAppStore()

const containerRef = ref<HTMLDivElement>()
const canvasRef = ref<HTMLCanvasElement>()

let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let controls: OrbitControls
let animationId: number

// Highlight state
const hoveredNode = ref<string | null>(null)
let raycaster = new THREE.Raycaster()
let mouse = new THREE.Vector2()

// Store meshes for interaction
const nodeMeshes: THREE.Mesh[] = []

// Compute statistics for the legend
const categoryStats = computed(() => {
  const stats = new Map<string, number>()
  NODE_CATEGORIES.forEach(c => stats.set(c, 0))
  
  knowledgeStore.nodes.forEach(node => {
    const count = stats.get(node.category) || 0
    stats.set(node.category, count + 1)
  })
  
  return Array.from(stats.entries())
    .filter(([_, count]) => count > 0)
    .map(([name, count], index) => {
      // Generate the same color as the 3D nodes
      const hue = (NODE_CATEGORIES.indexOf(name) / NODE_CATEGORIES.length) * 360
      return {
        name,
        count,
        color: `hsl(${hue}, 100%, 65%)`
      }
    })
})

const getCategoryColor = (category: string) => {
  const index = NODE_CATEGORIES.indexOf(category)
  const hue = index >= 0 ? (index / NODE_CATEGORIES.length) * 360 : 0
  return new THREE.Color(`hsl(${hue}, 100%, 65%)`)
}

const getCategoryHeight = (category: string) => {
  const index = NODE_CATEGORIES.indexOf(category)
  const normalized = index >= 0 ? index / NODE_CATEGORIES.length : 0
  // Vertical layering: younger/basic at bottom (-30), older/advanced at top (30)
  return normalized * 60 - 30
}

const initScene = () => {
  if (!canvasRef.value || !containerRef.value) return

  // Scene - Deep space background
  scene = new THREE.Scene()
  scene.background = new THREE.Color(0x02040a)
  scene.fog = new THREE.FogExp2(0x02040a, 0.015)

  // Camera - Cinematic perspective
  const aspect = containerRef.value.clientWidth / containerRef.value.clientHeight
  camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 1000)
  camera.position.set(0, 20, 80)
  camera.lookAt(0, 0, 0)

  // Renderer
  renderer = new THREE.WebGLRenderer({
    canvas: canvasRef.value,
    antialias: true,
    alpha: false,
    powerPreference: "high-performance"
  })
  renderer.setSize(containerRef.value.clientWidth, containerRef.value.clientHeight)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2)) // cap ratio for performance

  // Controls
  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.autoRotate = true
  controls.autoRotateSpeed = 0.5
  controls.maxDistance = 150
  controls.minDistance = 10

  // Lighting - Ethereal ambient light + directional highlights
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.4)
  scene.add(ambientLight)
  
  const dirLight1 = new THREE.DirectionalLight(0xffffff, 1.2)
  dirLight1.position.set(50, 50, 50)
  scene.add(dirLight1)

  const dirLight2 = new THREE.DirectionalLight(0x4444ff, 2.0)
  dirLight2.position.set(-50, -20, -50)
  scene.add(dirLight2)

  createKnowledgeNetwork()
  
  // Interaction
  renderer.domElement.addEventListener('mousemove', onMouseMove)
  renderer.domElement.addEventListener('click', onClick)

  animate()
}

const createKnowledgeNetwork = () => {
  const nodes = knowledgeStore.nodes
  const nodePositions = new Map<string, THREE.Vector3>()
  
  // 1. Create Nodes (Vibrant dots & glow)
  const sphereGeo = new THREE.SphereGeometry(1, 16, 16)
  
  nodes.forEach((node, i) => {
    const color = getCategoryColor(node.category)
    const baseHeight = getCategoryHeight(node.category)
    
    // Spread radially within height layer
    const radius = 10 + Math.random() * 35
    const angle = Math.random() * Math.PI * 2
    
    // Add some noise to height
    const y = baseHeight + (Math.random() - 0.5) * 10
    const x = Math.cos(angle) * radius
    const z = Math.sin(angle) * radius
    
    const pos = new THREE.Vector3(x, y, z)
    nodePositions.set(node.id, pos)
    
    // Core Mesh
    const mat = new THREE.MeshStandardMaterial({
      color,
      emissive: color,
      emissiveIntensity: 0.8,
      roughness: 0.2,
      metalness: 0.8
    })
    
    // Size based on importance
    const scale = 0.5 + (node.importance || 3) * 0.15
    const mesh = new THREE.Mesh(sphereGeo, mat)
    mesh.position.copy(pos)
    mesh.scale.setScalar(scale)
    mesh.userData = { id: node.id, category: node.category, color: color.getHex() }
    
    scene.add(mesh)
    nodeMeshes.push(mesh)
    
    // Glow Sprite (ethereal look)
    const glowMat = new THREE.SpriteMaterial({
      map: createRadialGradient(),
      color: color,
      transparent: true,
      opacity: 0.6,
      blending: THREE.AdditiveBlending,
      depthWrite: false
    })
    const glow = new THREE.Sprite(glowMat)
    glow.scale.setScalar(scale * 4)
    mesh.add(glow) // attach to core
  })

  // 2. Create Threads (Dense web of glowing lines)
  const edges = knowledgeStore.edges
  const lineMat = new THREE.LineBasicMaterial({
    color: 0xffffff,
    transparent: true,
    opacity: 0.15,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  })
  
  const lineGeo = new THREE.BufferGeometry()
  const linePositions: number[] = []
  const lineColors: number[] = []
  
  edges.forEach(edge => {
    const sourcePos = nodePositions.get(edge.source)
    const targetPos = nodePositions.get(edge.target)
    
    if (sourcePos && targetPos) {
      const sourceNode = nodes.find(n => n.id === edge.source)
      const targetNode = nodes.find(n => n.id === edge.target)
      
      const c1 = sourceNode ? getCategoryColor(sourceNode.category) : new THREE.Color(0xffffff)
      const c2 = targetNode ? getCategoryColor(targetNode.category) : new THREE.Color(0xffffff)
      
      linePositions.push(sourcePos.x, sourcePos.y, sourcePos.z)
      linePositions.push(targetPos.x, targetPos.y, targetPos.z)
      
      lineColors.push(c1.r, c1.g, c1.b)
      lineColors.push(c2.r, c2.g, c2.b)
    }
  })
  
  lineGeo.setAttribute('position', new THREE.Float32BufferAttribute(linePositions, 3))
  lineGeo.setAttribute('color', new THREE.Float32BufferAttribute(lineColors, 3))
  
  // Use vertex colors for gradient lines
  const gradientLineMat = new THREE.LineBasicMaterial({
    vertexColors: true,
    transparent: true,
    opacity: 0.25,
    blending: THREE.AdditiveBlending,
    depthWrite: false
  })
  
  const lines = new THREE.LineSegments(lineGeo, gradientLineMat)
  scene.add(lines)
}

// Generate radial gradient for glows
const createRadialGradient = () => {
  const canvas = document.createElement('canvas')
  canvas.width = 64
  canvas.height = 64
  const ctx = canvas.getContext('2d')
  if (ctx) {
    const gradient = ctx.createRadialGradient(32, 32, 0, 32, 32, 32)
    gradient.addColorStop(0, 'rgba(255,255,255,1)')
    gradient.addColorStop(0.2, 'rgba(255,255,255,0.8)')
    gradient.addColorStop(1, 'rgba(255,255,255,0)')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, 64, 64)
  }
  return new THREE.CanvasTexture(canvas)
}

const onMouseMove = (event: MouseEvent) => {
  if (!canvasRef.value) return
  const rect = canvasRef.value.getBoundingClientRect()
  mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1
  mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1
}

const onClick = () => {
  raycaster.setFromCamera(mouse, camera)
  const intersects = raycaster.intersectObjects(nodeMeshes)
  
  if (intersects.length > 0) {
    const clickedNodeId = intersects[0].object.userData.id
    appStore.openPanel(clickedNodeId)
  }
}

const animate = () => {
  animationId = requestAnimationFrame(animate)
  
  // If panel is open, drop framerate or pause heavy rotations (simulated by damping controls only)
  // Actually, we'll just slow down auto-rotate
  controls.autoRotateSpeed = appStore.panelOpen ? 0.1 : 0.5
  
  // Handle hover highlighting
  raycaster.setFromCamera(mouse, camera)
  const intersects = raycaster.intersectObjects(nodeMeshes)
  
  if (intersects.length > 0) {
    document.body.style.cursor = 'pointer'
    const obj = intersects[0].object as THREE.Mesh
    hoveredNode.value = knowledgeStore.getNodeById(obj.userData.id)?.name || null
    
    // Scale up slightly on hover
    obj.scale.setScalar(obj.scale.x * 0.9 + 1.2 * 0.1) 
  } else {
    document.body.style.cursor = 'default'
    hoveredNode.value = null
  }

  controls.update()
  renderer.render(scene, camera)
}

const handleResize = () => {
  if (!containerRef.value) return
  camera.aspect = containerRef.value.clientWidth / containerRef.value.clientHeight
  camera.updateProjectionMatrix()
  renderer.setSize(containerRef.value.clientWidth, containerRef.value.clientHeight)
}

onMounted(() => {
  initScene()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  cancelAnimationFrame(animationId)
  window.removeEventListener('resize', handleResize)
  renderer.dispose()
  document.body.style.cursor = 'default'
})
</script>

<template>
  <div ref="containerRef" class="universe-container">
    <canvas ref="canvasRef" class="universe-canvas" />
    
    <!-- Cinematic Overlay Gradients -->
    <div class="vignette" />

    <!-- Hover Tooltip -->
    <div 
      v-if="hoveredNode && !appStore.panelOpen" 
      class="hover-tooltip"
      :style="{ left: `calc(50% + ${(mouse.x * 50)}vw)`, top: `calc(50% - ${(mouse.y * 50)}vh - 30px)` }"
    >
      {{ hoveredNode }}
    </div>

    <!-- Legend (Left Side) -->
    <div class="legend-panel glass-dark">
      <h3 class="legend-title">Subject Taxonomy</h3>
      <div class="legend-list">
        <div v-for="stat in categoryStats" :key="stat.name" class="legend-item">
          <span class="legend-dot" :style="{ backgroundColor: stat.color, boxShadow: `0 0 8px ${stat.color}` }" />
          <span class="legend-name">{{ stat.name }}</span>
          <span class="legend-count">{{ stat.count }}</span>
        </div>
      </div>
    </div>
    
    <!-- Title / Instructions -->
    <div class="universe-title">
      <h1>Knowledge Universe</h1>
      <p>Explore the vast network of Python skills.</p>
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
  background: #02040a;
}

.universe-canvas {
  width: 100%;
  height: 100%;
  display: block;
}

/* Cinematic vignette effect */
.vignette {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(circle at center, transparent 40%, rgba(0,0,0,0.8) 100%);
  z-index: 1;
}

/* Hover Tooltip */
.hover-tooltip {
  position: absolute;
  pointer-events: none;
  background: rgba(255, 255, 255, 0.9);
  color: #000;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  transform: translate(-50%, -100%);
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0,0,0,0.5);
  white-space: nowrap;
}

/* Legend */
.legend-panel {
  position: absolute;
  left: 32px;
  top: 50%;
  transform: translateY(-50%);
  z-index: 5;
  padding: 24px;
  border-radius: var(--radius-lg);
  width: 260px;
  max-height: 80vh;
  overflow-y: auto;
}

.legend-title {
  font-size: 14px;
  font-weight: 700;
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-bottom: 16px;
  color: rgba(255,255,255,0.9);
}

.legend-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.legend-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-name {
  flex: 1;
  font-size: 13px;
  color: rgba(255,255,255,0.7);
}

.legend-count {
  font-size: 12px;
  font-family: var(--font-mono);
  color: rgba(255,255,255,0.5);
}

/* Title */
.universe-title {
  position: absolute;
  top: 32px;
  left: 32px;
  z-index: 5;
  pointer-events: none;
}

.universe-title h1 {
  font-size: 32px;
  font-weight: 800;
  letter-spacing: -0.5px;
  color: #fff;
  text-shadow: 0 2px 10px rgba(0,0,0,0.5);
  margin-bottom: 4px;
}

.universe-title p {
  font-size: 14px;
  color: rgba(255,255,255,0.6);
}
</style>