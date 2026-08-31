export default function Header({ title }: { title: string }) {
  return (
    <header className="flex h-14 shrink-0 items-center border-b border-neutral-800 bg-neutral-950 px-4">
      <div className="flex items-center gap-2">
        <div className="h-2 w-2 rounded-full bg-emerald-400" />
        <h1 className="text-sm font-medium text-neutral-200">{title}</h1>
      </div>
    </header>
  );
}
