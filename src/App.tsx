import { NbaPredictor } from './components/NbaPredictor';

function App() {
  return (
    // CONTENEDOR PRINCIPAL
    <div className="min-h-screen relative bg-black font-sans selection:bg-orange-500 selection:text-white">
      
      {/* 1. IMAGEN DE FONDO (NBA Vibe) */}
      <div 
        className="fixed inset-0 z-0"
        style={{
          // Foto de cancha de basket profesional
          backgroundImage: "url('https://images.unsplash.com/photo-1546519638-68e109498ffc?q=80&w=2090&auto=format&fit=crop')",
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          // Trucos de diseño: Oscurecer (brightness) y desenfocar (blur) para que se lea el texto
          filter: 'brightness(0.3) blur(3px)' 
        }}
      />

      {/* 2. CAPA DE CONTENIDO (Flotando encima) */}
      <div className="relative z-10 flex flex-col items-center min-h-screen p-4 overflow-y-auto">
        
        {/* TÍTULO DEL PROYECTO */}
        <div className="mt-10 mb-8 text-center animate-fade-in-down">
          <h1 className="text-6xl md:text-7xl font-black tracking-tighter text-transparent bg-clip-text bg-gradient-to-r from-orange-500 via-amber-500 to-red-600 drop-shadow-[0_2px_10px_rgba(234,88,12,0.5)]">
            CUY APOSTADOR
          </h1>
          
          <div className="mt-4 inline-flex items-center gap-2 bg-black/40 backdrop-blur-md px-6 py-2 rounded-full border border-white/10 shadow-lg">
            <span className="relative flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
            </span>
            <p className="text-slate-200 font-medium tracking-wide text-sm">
              Sistema de Análisis de Riesgo Deportivo
            </p>
          </div>
        </div>

        {/* TU COMPONENTE MAESTRO */}
        <div className="w-full animate-fade-in-up">
          <NbaPredictor />
        </div>

        {/* PIE DE PÁGINA */}
        <footer className="mt-16 mb-6 text-center">
          <p className="text-slate-500 text-xs">
            Desarrollado con <span className="text-yellow-500">Python</span> & <span className="text-blue-400">React</span>
          </p>
          <p className="text-slate-600 text-[10px] mt-1 uppercase tracking-widest">
            Modelo SGD • Análisis de Sensibilidad • Gestión de Stake
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;