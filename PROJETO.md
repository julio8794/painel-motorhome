# Painel Motorhome — anotações do projeto

Painel único para os aparelhos Bluetooth do motorhome. Mesma base de código em dois formatos:

- **Web/PWA:** `index.html` publicado no GitHub Pages — https://julio8794.github.io/painel-motorhome/
- **App Android (APK):** Capacitor em `android-app/`, gerado automaticamente pelo GitHub Actions a cada push.
  Download fixo: https://github.com/julio8794/painel-motorhome/releases/latest/download/PainelMotorhome.apk

## Estrutura

| Caminho | O que é |
|---|---|
| `index.html` | Todo o painel (HTML+CSS+JS). Usado pelo site e copiado para dentro do APK. |
| `sw.js`, `manifest.webmanifest`, `icons/` | PWA (offline, instalação). Subir `VERSION` no `sw.js` e `APP_VER` no `index.html` a cada versão. |
| `android-app/` | Projeto Capacitor 8: `package.json`, `capacitor.config.json`, `native/` (Java + recursos), `scripts/patch_android.py`, `signing/` (chave fixa de assinatura). |
| `.github/workflows/android.yml` | Compila, assina e publica o APK como release `app-vN`. |

No app Android, `index.html` detecta `window.Capacitor` e troca o Web Bluetooth por uma camada sobre o plugin
`@capacitor-community/bluetooth-le`. O serviço em primeiro plano (`MonitorService`, plugin `KeepAlive`) mantém o app
conectado em segundo plano; alertas usam `@capacitor/local-notifications`.

## Protocolos (extraídos dos apps oficiais)

### Monitor de bateria Junctek KG (app "KG", com.juntek.kg / com.juntek.vat)
- Serviço `FFF0`; notificação `FFF1`; escrita `FFF2`.
- Quadros `BB … EE`. Valores em BCD seguidos de um byte-etiqueta ≥ 0xA0. Pedido de tudo: `BB 9A A9 10 EE`.
- Etiquetas: `C0` V/100 · `C1` A/100 · `D1` direção (1 = carregando) · `D2` Ah restantes/1000 · `B0` capacidade/10 ·
  `D8` W/100 · `D6` minutos restantes · `D9` temp−100 · `D3` Ah acumulados/1000 · `D4` kWh/100000 · `D5` segundos ·
  `D7` resistência mΩ/100 · `D0` relé (0 ligado, 99 desligado, 1–7 proteções) · `E0` modelo.
- Escrita: `BB` + (valor BCD + etiqueta)… + checksum (soma % 100 em BCD) + `EE`.
  Capacidade `Ah*10 → B0`; carga `Ah*1000 → D2`; relé `0/99 → D0`; zerar corrente `99 → A4`; zerar dados `0 → A3`.

### BMS Daly (app "SMART BMS", com.inuker.bluetooth.daliy) — série H/K/M/S
- Serviço `FFF0`; notificação `FFF1`; escrita `FFF2`.
- Leitura: `D2 03 00 00 00 3E D7 B9` (Modbus, CRC16 0xA001, byte baixo primeiro). Resposta `D2 03 7C` + 62 registradores.
- Registradores: 0–31 células mV · 32–39 temp−40 · 40 V/10 · 41 (A−30000)/10 (positivo = carregando) · 42 SOC/10 ·
  43 célula máx mV · 44 célula mín mV · 48 Ah/10 · 49 nº células · 50 nº sensores · 51 ciclos · 53 MOS carga ·
  54 MOS descarga · 56 diferença mV · 57 potência W.

### Carregador OLYS (app "ChargerConnect", com.olys.olysble)
- Serviço `18F0`; notificação `2AF0`; escrita `2AF1`.
- Comandos: tipo `FF E1 01 E2`, dados `FF E2 02 E4`, batimento `FF C2 02 C4` (a cada 2 s).
- Resposta `FF E2` + 38 bytes (checksum = soma dos bytes 2..38). Bytes: 2–3 A bat/10 · 4–5 V bat/100 ·
  6–9 bateria auxiliar · 10–11 W solar · 12–13 V solar/10 · 14–19 saída de carga · 20 / 34–35 V bateria do motor/10 ·
  21 estado (bit6 carregando, bit4 cheio, bits 3..0 falhas invertidas) · 22–24 Ah · 25–27 Wh · 36–37 V saída/10 · 38 A máx.

### Climatizador Resfri Ar (app "Resfri Ar", br.com.resfriar.resfriar_connect — Flutter)
- Serviço `6e400001-b5a3-f393-e0a9-e50e24dcca9e`; um canal por grandeza, valores em **texto**:
  `…0002` ventilador 0–100 (0 = desligado) · `…0003` modo 0 ventilar / 1 resfriar / 2 conforto ·
  `…0005` timer 0–5 h · `…0008` luz · `…0006` versão · `…0007` modelo · `…0012` erro
  (1 motor em curto, 2 sobrecarga no motor, 3 bomba do tanque, 4 bomba de retorno, 6 load dump, 9 circuito de detecção).
- Desligar: modo "0", timer "0", ventilador "0". Ligar: ventilador (último %) e modo (último).
