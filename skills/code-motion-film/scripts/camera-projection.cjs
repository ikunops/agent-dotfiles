// camera-projection.cjs — 逐帧相机投影 + 假运镜检测
//
// 目的：让"平面画法也能环绕/升降/推拉"落到代码上，而不是只写在文档里。
// 做法：物体用 3D 点表示，每帧由相机参数投影到 2D，按深度排序后绘制。
// 这样平面色块也能读出体积，因为轮廓每一帧都在变。
//
// 依赖：无。纯函数 + 一个自测。

const DEG = Math.PI / 180;

// 相机：绕 Y 轴方位角 yaw，俯仰 pitch，距离 dist，焦距 fov(度)，注视点 target
function makeCamera({yaw = 0, pitch = 0, dist = 6, fov = 50, target = [0, 0, 0], up = [0, 1, 0]} = {}) {
  const cy = Math.cos(yaw * DEG), sy = Math.sin(yaw * DEG);
  const cp = Math.cos(pitch * DEG), sp = Math.sin(pitch * DEG);

  // 视线方向（从相机指向目标）
  const fwd = [sy * cp, -sp, -cy * cp];
  // 相机位置 = 目标 - fwd * dist
  const pos = [target[0] - fwd[0] * dist, target[1] - fwd[1] * dist, target[2] - fwd[2] * dist];

  // right = normalize(cross(fwd, up))
  let right = cross(fwd, up);
  right = norm(right);
  // trueUp = cross(right, fwd)
  const tUp = cross(right, fwd);

  return {pos, fwd, right, up: tUp, fov, dist, target};
}

function cross(a, b) {
  return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
}
function dot(a, b) { return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]; }
function sub(a, b) { return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]; }
function norm(a) { const l = Math.hypot(a[0], a[1], a[2]) || 1; return [a[0] / l, a[1] / l, a[2] / l]; }

// 把世界坐标点投到画布。返回 {x, y, depth, visible}
function project(cam, p, {width, height}) {
  const rel = sub(p, cam.pos);
  const x = dot(rel, cam.right);
  const y = dot(rel, cam.up);
  const z = dot(rel, cam.fwd); // 沿视线方向的深度
  if (z <= 0.001) return {x: 0, y: 0, depth: z, visible: false};

  const f = 1 / Math.tan((cam.fov * DEG) / 2);
  const ndcX = (x / z) * f;
  const ndcY = (y / z) * f;
  // 保持竖屏/横屏比例：以短边为基准
  const scale = Math.min(width, height) * 0.5;
  return {
    x: width / 2 + ndcX * scale,
    y: height / 2 - ndcY * scale,
    depth: z,
    visible: true,
  };
}

// 柱体：底心 + 半径 + 高 + 分段数。返回按深度排好序的面（画家算法）。
function cylinder({base, radius, height, segments = 12, axis = "y"}) {
  const [bx, by, bz] = base;
  const rings = [];
  for (let i = 0; i < segments; i++) {
    const a = (i / segments) * Math.PI * 2;
    const c = Math.cos(a), s = Math.sin(a);
    rings.push({
      angle: a,
      bottom: axis === "y" ? [bx + c * radius, by, bz + s * radius] : [bx + c * radius, by + s * radius, bz],
      top: axis === "y" ? [bx + c * radius, by + height, bz + s * radius] : [bx + c * radius, by + s * radius, bz + height],
    });
  }
  const faces = [];
  for (let i = 0; i < segments; i++) {
    const a = rings[i], b = rings[(i + 1) % segments];
    faces.push({kind: "side", points: [a.bottom, b.bottom, b.top, a.top], normalAngle: (a.angle + b.angle) / 2});
  }
  return {rings, faces};
}

// 画一个场景：所有面先投影，剔背面，按深度从远到近排序
function renderScene(cam, faces, size) {
  const out = [];
  for (const f of faces) {
    const pts = f.points.map((p) => project(cam, p, size));
    if (pts.some((p) => !p.visible)) continue;
    const depth = pts.reduce((s, p) => s + p.depth, 0) / pts.length;
    const area = polygonArea(pts);
    if (area < 0.5) continue;
    out.push({...f, pts, depth, area});
  }
  out.sort((a, b) => b.depth - a.depth); // 远的先画
  return out;
}

function polygonArea(pts) {
  let s = 0;
  for (let i = 0; i < pts.length; i++) {
    const a = pts[i], b = pts[(i + 1) % pts.length];
    s += a.x * b.y - b.x * a.y;
  }
  return Math.abs(s) / 2;
}

// 形状签名：把顶点按包围盒归一化，得到一组 [0,1] 坐标。
// 平移、等比缩放都不改变签名；只有形真的变了才变。
function silhouettePoints(faces) {
  const pts = [];
  for (const f of faces) for (const p of f.pts) pts.push(p);
  const xs = pts.map((p) => p.x), ys = pts.map((p) => p.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const w = Math.max(maxX - minX, 1e-6), h = Math.max(maxY - minY, 1e-6);
  return pts.map((p) => [(p.x - minX) / w, (p.y - minY) / h]);
}

// 归一化后的最近邻平均距离：0 = 形完全没变，越大 = 形变得越多
function shapeDiff(a, b) {
  let sum = 0;
  for (const p of a) {
    let best = Infinity;
    for (const q of b) {
      const d = Math.hypot(p[0] - q[0], p[1] - q[1]);
      if (d < best) best = d;
    }
    sum += best;
  }
  return sum / Math.max(a.length, 1);
}

// 自测：环绕时形必须变，整层平移时形不变
function selftest() {
  const size = {width: 1920, height: 1080};
  const obj = cylinder({base: [0, -1, 0], radius: 1, height: 2, segments: 16});
  let ok = true;
  const sigs = [];
  for (const yaw of [0, 30, 60, 90]) {
    const cam = makeCamera({yaw, pitch: 12, dist: 7});
    const faces = renderScene(cam, obj.faces, size);
    if (faces.length === 0) { console.error("yaw", yaw, "无可见面"); ok = false; }
    // 用最靠前的一个侧面的轮廓当签名
    sigs.push(silhouettePoints(faces));
  }
  const diffs = [];
  for (let i = 1; i < sigs.length; i++) diffs.push(shapeDiff(sigs[i - 1], sigs[i]));
  const changed = diffs.filter((d) => d > 0.02).length;
  console.log("轮廓变化（相邻两帧）:", diffs.map((d) => d.toFixed(3)).join(", "));
  if (changed < 2) { console.error("FAIL: 环绕时轮廓没有明显变化，像纸片翻转"); ok = false; }

  // 纯平移：形不变
  const a = renderScene(makeCamera({yaw: 0, pitch: 12, dist: 7}), obj.faces, size);
  const shifted = a.map((f) => ({pts: f.pts.map((p) => ({x: p.x + 200, y: p.y}))}));
  const translatedSig = silhouettePoints(shifted);
  const d = shapeDiff(sigs[0], translatedSig);
  console.log("平移后轮廓差:", d.toFixed(3));
  if (d > 0.01) { console.error("FAIL: 平移不该改变归一化轮廓"); ok = false; }

  console.log(ok ? "PASS" : "FAILED");
  return ok;
}

if (require.main === module) {
  if (process.argv.includes("--selftest")) process.exit(selftest() ? 0 : 1);
  console.log("用法: node camera-projection.cjs --selftest");
}

module.exports = {makeCamera, project, cylinder, renderScene, silhouettePoints, shapeDiff, DEG};
