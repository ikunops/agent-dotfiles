import { useState } from 'react';
import { useFloating, autoPlacement, useDismiss } from '@floating-ui/react';

const SCOPES = ['global', 'page', 'entity', 'sub-entity'];

export default function App() {
  const [scope, setScope] = useState('page');
  const [depth, setDepth] = useState(3);
  const [open, setOpen] = useState(false);

  const strategy = resolveStrategy(scope, depth);

  const { refs, context } = useFloating({
    open,
    onOpenChange: setOpen,
    placement: open ? 'right' : undefined,
    middleware: [autoPlacement({ allowedPlacements: ['right','bottom','left','top'] })],
  });

  const status = !strategy.risk ? 'LEGAL' : `⚠ ${strategy.risk}`;

  return (
    <div className="p-6 font-mono text-sm">
      <header className="mb-6 flex gap-6">
        <label>
          Scope:
          <select value={scope} onChange={e => setScope(e.target.value)} data-scope={scope} className="ml-2">
            {SCOPES.map(s => <option key={s} value={s}>{s}</option>)}
          </select>
        </label>
        <label>
          Nesting depth:
          <input type="range" min="1" max="6" value={depth} onChange={e => setDepth(+e.target.value)} className="align-middle" />
          <span className="ml-2">{depth}</span>
        </label>
        <button ref={refs.setReference} onClick={() => setOpen(!open)} data-z-layer={strategy.cap}>
          Trigger menu
        </button>
      </header>

      <div className="mt-4 rounded bg-zinc-100 p-3">
        <strong>Applied Strategy:</strong> {strategy.label}
        <br />Z-layer cap (scope '{scope}'): {strategy.cap}
        <br />Parent overflow: {strategy.parent}
        <br />Portal restack: {strategy.portal}
        <br />Edge flip: {strategy.flip}
      </div>

      {open && (
        <div
          ref={refs.setFloating}
          data-portal
          className="z-20 rounded-md border border-blue-500 bg-white p-3 shadow-xl"
          style={{ position: strategy.parent === 'fixed' ? 'fixed' : 'absolute' }}
        >
          Floating menu — scope-aware placement
          <div className="mt-2 rounded bg-green-100 p-1">{status}</div>
        </div>
      )}
    </div>
  );
}

/** strategy lookup mirrors strategies.md */
function resolveStrategy(scope, depth) {
  const cap = {
    global: 50,
    page: 30,
    entity: 20,
    sub-entity: 10,
  };
  let risk = '';
  let label = '';
  if (depth <= 1 || scope === 'global') {
    label = 'fixed / overflow-visible / global top-layer';
  } else if (scope === 'page' || depth === 2) {
    label = 'overlay / modal / scroll-lock';
  } else if (scope === 'entity') {
    if (depth > 2) risk = 'depth>2 with entity scope → overflow-auto parent must use position-fixed';
    label = 'entity surface / auto-flip on edge';
  } else {
    label = 'sub-entity menu / portal-restack required';
    if (depth > 4) risk = 'too deep → consider flattening';
  }
  return { cap: cap[scope], parent: depth > 2 ? 'fixed' : 'relative', portal: depth < 3 ? 'no' : 'yes', flip: depth >= 2 ? 'yes' : 'no', label, risk };
}
