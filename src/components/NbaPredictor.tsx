import { useState, useMemo } from 'react';
import myPredictions from '../data/nba_predictions.json';

// Diccionario de Nombres
const teamNames: Record<string, string> = {
  "ATL": "Atlanta Hawks",
  "BOS": "Boston Celtics",
  "BKN": "Brooklyn Nets",
  "CHA": "Charlotte Hornets",
  "CHI": "Chicago Bulls",
  "CLE": "Cleveland Cavaliers",
  "DAL": "Dallas Mavericks",
  "DEN": "Denver Nuggets",
  "DET": "Detroit Pistons",
  "GSW": "Golden State Warriors",
  "HOU": "Houston Rockets",  // <--- ¡AQUÍ ESTÁ EL IMPORTANTE!
  "IND": "Indiana Pacers",
  "LAC": "LA Clippers",
  "LAL": "Los Angeles Lakers",
  "MEM": "Memphis Grizzlies",
  "MIA": "Miami Heat",
  "MIL": "Milwaukee Bucks",
  "MIN": "Minnesota Timberwolves",
  "NOP": "New Orleans Pelicans",
  "NYK": "New York Knicks",
  "OKC": "Oklahoma City Thunder",
  "ORL": "Orlando Magic",
  "PHI": "Philadelphia 76ers",
  "PHX": "Phoenix Suns",
  "POR": "Portland Trail Blazers",
  "SAC": "Sacramento Kings",
  "SAS": "San Antonio Spurs",
  "TOR": "Toronto Raptors",
  "UTA": "Utah Jazz",
  "WAS": "Washington Wizards"
};

// Interfaces
interface LocalData {
  player: string;
  team: string;
  points: number;    // Predicción IA
  floor: number;     // Piso
  ceiling: number;   // Techo
  real_pts: number;
}

interface AnalyzedPlayer {
  data: LocalData;
  line: number;
  advice: string;      // OVER / UNDER
  status: 'SAFE' | 'RISKY';
  diff: number;        // Diferencia clave
}

export function NbaPredictor() {
  // Estados para Selección de Equipos
  const [homeTeam, setHomeTeam] = useState('');
  const [awayTeam, setAwayTeam] = useState('');
  
  // Estado para las líneas de Stake (Mapa: "NombreJugador" -> "ValorStake")
  const [stakes, setStakes] = useState<Record<string, string>>({});
  
  // Estado para mostrar resultados
  const [results, setResults] = useState<AnalyzedPlayer[] | null>(null);

  // 1. OBTENER LISTA ÚNICA DE EQUIPOS
  const allTeams = useMemo(() => {
    const teams = new Set((myPredictions as LocalData[]).map(p => p.team));
    return Array.from(teams).sort();
  }, []);

  // 2. FILTRAR JUGADORES POR EQUIPO SELECCIONADO
  const homePlayers = useMemo(() => 
    (myPredictions as LocalData[]).filter(p => p.team === homeTeam).sort((a,b) => b.points - a.points),
  [homeTeam]);

  const awayPlayers = useMemo(() => 
    (myPredictions as LocalData[]).filter(p => p.team === awayTeam).sort((a,b) => b.points - a.points),
  [awayTeam]);

  // Manejar cambios en los inputs de Stake
  const handleStakeChange = (player: string, value: string) => {
    setStakes(prev => ({ ...prev, [player]: value }));
  };

  // 3. LÓGICA DE ANÁLISIS (EL CEREBRO)
  const analyzeMatchup = () => {
    const analyzed: AnalyzedPlayer[] = [];
    const allSelectedPlayers = [...homePlayers, ...awayPlayers];

    allSelectedPlayers.forEach(player => {
      const stakeStr = stakes[player.player];
      // Solo analizamos si el usuario escribió un número
      if (stakeStr && stakeStr.trim() !== '') {
        const line = parseFloat(stakeStr);
        let advice = "PASS";
        let status: 'SAFE' | 'RISKY' = 'RISKY';
        let diff = 0;

        // Lógica de Techo/Piso
        if (line < player.floor) {
          advice = "OVER ⬆️";
          status = 'SAFE'; // Línea debajo del peor escenario -> Muy seguro
          diff = player.points - line;
        } else if (line > player.ceiling) {
          advice = "UNDER ⬇️";
          status = 'SAFE'; // Línea encima del mejor escenario -> Muy seguro
          diff = line - player.points;
        } else {
          // Dentro del rango de incertidumbre
          advice = line < player.points ? "OVER (Riesgo)" : "UNDER (Riesgo)";
          status = 'RISKY';
          diff = Math.abs(player.points - line);
        }

        analyzed.push({
          data: player,
          line,
          advice,
          status,
          diff
        });
      }
    });

    // Ordenar por seguridad (SAFE primero) y luego por mayor diferencia
    analyzed.sort((a, b) => {
      if (a.status === b.status) return b.diff - a.diff;
      return a.status === 'SAFE' ? -1 : 1;
    });

    setResults(analyzed);
  };

  const resetAnalysis = () => {
    setResults(null);
    setStakes({});
  };

  // --- VISTA DE RESULTADOS ---
  if (results) {
    return (
      <div className="w-full max-w-6xl mx-auto p-4 animate-fade-in">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-3xl font-black text-white italic">RESULTADOS DEL ANÁLISIS</h2>
          <button onClick={() => setResults(null)} className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg font-bold">
            ← VOLVER A EDITAR
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {results.map((res) => (
            <div key={res.data.player} className={`relative p-5 rounded-xl border-2 ${res.status === 'SAFE' ? 'bg-slate-900 border-green-500 shadow-[0_0_15px_rgba(34,197,94,0.3)]' : 'bg-slate-900 border-slate-700 opacity-80'}`}>
              
              {/* Etiqueta de Seguridad */}
              <div className={`absolute top-0 right-0 px-3 py-1 rounded-bl-lg text-xs font-black uppercase ${res.status === 'SAFE' ? 'bg-green-500 text-black' : 'bg-yellow-600 text-white'}`}>
                {res.status === 'SAFE' ? 'APUESTA SEGURA' : 'ARRIESGADA'}
              </div>

              <h3 className="text-xl font-bold text-white truncate pr-20">{res.data.player}</h3>
              <p className="text-sm text-slate-400 mb-4">{res.data.team} • Promedio Real: {res.data.real_pts}</p>

              <div className="flex justify-between items-end mb-4 border-b border-slate-700 pb-4">
                <div className="text-center">
                  <span className="text-xs text-slate-500 uppercase">Línea</span>
                  <p className="text-2xl font-bold text-blue-400">{res.line}</p>
                </div>
                <div className="text-center">
                  <span className="text-xs text-slate-500 uppercase">EL CUY APOSTADOR</span>
                  <p className="text-3xl font-black text-orange-500">{res.data.points}</p>
                </div>
              </div>

              <div className="text-center">
                <p className="text-xs text-slate-500 mb-1">Recomendación</p>
                <div className={`text-2xl font-black ${res.advice.includes('OVER') ? 'text-green-400' : 'text-red-400'}`}>
                  {res.advice}
                </div>
                <div className="mt-2 text-xs text-slate-400 flex justify-between px-4">
                   <span>Piso: {res.data.floor}</span>
                   <span>Techo: {res.data.ceiling}</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // --- VISTA DE SELECCIÓN (INPUTS) ---
  return (
    <div className="w-full max-w-7xl mx-auto p-4 space-y-6">
      
      {/* HEADER: SELECTORES DE EQUIPO */}
      <div className="bg-slate-900 p-6 rounded-2xl border border-slate-800 shadow-xl">
        <div className="flex flex-col md:flex-row gap-6 items-center justify-between">
          
          {/* LOCAL */}
          <div className="flex-1 w-full">
            <label className="block text-slate-400 text-xs uppercase font-bold mb-2">Equipo Local (Home)</label>
            <select 
              className="w-full bg-slate-800 text-white p-3 rounded-lg border border-slate-700 focus:border-blue-500 outline-none font-bold text-lg"
              value={homeTeam}
              onChange={(e) => setHomeTeam(e.target.value)}
            >
              <option value="">-- Seleccionar --</option>
              {allTeams.map(t => <option key={t} value={t}>{teamNames[t] || t}</option>)}
            </select>
          </div>

          <div className="text-2xl font-black text-slate-600">VS</div>

          {/* VISITANTE */}
          <div className="flex-1 w-full">
            <label className="block text-slate-400 text-xs uppercase font-bold mb-2">Equipo Visitante (Away)</label>
            <select 
              className="w-full bg-slate-800 text-white p-3 rounded-lg border border-slate-700 focus:border-orange-500 outline-none font-bold text-lg"
              value={awayTeam}
              onChange={(e) => setAwayTeam(e.target.value)}
            >
              <option value="">-- Seleccionar --</option>
              {allTeams.map(t => <option key={t} value={t}>{teamNames[t] || t}</option>)}
            </select>
          </div>
        </div>
      </div>

      {/* LISTAS DE JUGADORES */}
      {homeTeam && awayTeam && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 animate-fade-in-up">
          
          {/* TABLA LOCAL */}
          <TeamTable 
            teamName={homeTeam} 
            players={homePlayers} 
            stakes={stakes} 
            onStakeChange={handleStakeChange} 
            color="blue"
          />

          {/* TABLA VISITANTE */}
          <TeamTable 
            teamName={awayTeam} 
            players={awayPlayers} 
            stakes={stakes} 
            onStakeChange={handleStakeChange} 
            color="orange"
          />

        </div>
      )}

      {/* BOTÓN DE ACCIÓN FLOTANTE */}
      {homeTeam && awayTeam && (
        <div className="sticky bottom-6 flex justify-center pt-4">
          <button 
            onClick={analyzeMatchup}
            className="bg-gradient-to-r from-blue-600 to-orange-600 hover:from-blue-500 hover:to-orange-500 text-white font-black py-4 px-12 rounded-full shadow-[0_0_20px_rgba(0,0,0,0.5)] transform hover:scale-105 transition-all text-xl border-4 border-slate-900"
          >
             PREDECIR PARTIDO
          </button>
        </div>
      )}
    </div>
  );
}

// Componente auxiliar para la tabla de jugadores (para no repetir código)
function TeamTable({ teamName, players, stakes, onStakeChange, color }: any) {
  const borderColor = color === 'blue' ? 'border-blue-600' : 'border-orange-600';
  const textColor = color === 'blue' ? 'text-blue-400' : 'text-orange-400';

  return (
    <div className={`bg-slate-900 rounded-xl overflow-hidden border-t-4 ${borderColor} shadow-lg`}>
      <div className="p-4 bg-slate-800/50 border-b border-slate-800 flex justify-between items-center">
        <h3 className={`text-xl font-black ${textColor}`}>{teamName}</h3>
        <span className="text-xs text-slate-500">{players.length} Jugadores</span>
      </div>
      <div className="max-h-[500px] overflow-y-auto">
        <table className="w-full text-left text-slate-300">
          <thead className="bg-slate-800 text-xs uppercase text-slate-500 sticky top-0">
            <tr>
              <th className="p-3">Jugador</th>
              <th className="p-3 w-32 text-center">Línea (Stake)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {players.map((p: any) => (
              <tr key={p.player} className="hover:bg-slate-800/50 transition-colors">
                <td className="p-3">
                  <div className="font-bold text-white">{p.player}</div>
                  <div className="text-xs text-slate-500">Pred: {p.points} pts</div>
                </td>
                <td className="p-3 text-center">
                  <input 
                    type="number" 
                    placeholder="-"
                    className="w-20 bg-black/30 border border-slate-600 rounded p-2 text-center text-white focus:border-white outline-none"
                    value={stakes[p.player] || ''}
                    onChange={(e) => onStakeChange(p.player, e.target.value)}
                    onWheel={(e) => e.currentTarget.blur()} // Evita cambio al scroll
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}