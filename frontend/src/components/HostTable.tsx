import { Host, STAGE_COLORS } from '../types';

interface Props {
  hosts: Host[];
}

export function HostTable({ hosts }: Props) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead className="bg-slate-800">
          <tr>
            <th className="px-4 py-2 text-left text-gray-300">IP Address</th>
            <th className="px-4 py-2 text-left text-gray-300">Role</th>
            <th className="px-4 py-2 text-left text-gray-300">Status</th>
            <th className="px-4 py-2 text-left text-gray-300">Last Seen</th>
            <th className="px-4 py-2 text-left text-gray-300">Peers</th>
          </tr>
        </thead>
        <tbody>
          {hosts.map((host) => (
            <tr key={host.ip} className="border-t border-slate-700 hover:bg-slate-800/50">
              <td className="px-4 py-2 font-mono text-blue-400">{host.ip}</td>
              <td className="px-4 py-2 text-gray-300">{host.role}</td>
              <td className="px-4 py-2">
                <span
                  className="px-2 py-1 rounded text-xs font-medium text-white"
                  style={{ backgroundColor: STAGE_COLORS[host.compromise_status] || '#6b7280' }}
                >
                  {host.compromise_status}
                </span>
              </td>
              <td className="px-4 py-2 text-gray-400">{host.last_seen}</td>
              <td className="px-4 py-2 text-gray-400">{host.connected_peers || 0}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
