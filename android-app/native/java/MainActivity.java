package br.julio.painelmotorhome;

import android.os.Build;
import android.os.Bundle;
import android.webkit.WebView;
import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        registerPlugin(KeepAlivePlugin.class);
        super.onCreate(savedInstanceState);
        WebView wv = webView();
        if (wv != null && Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            // mantém o JavaScript do painel com prioridade mesmo com o app minimizado
            wv.setRendererPriorityPolicy(WebView.RENDERER_PRIORITY_IMPORTANT, false);
        }
    }

    private WebView webView() {
        try { return getBridge() != null ? getBridge().getWebView() : null; } catch (Exception e) { return null; }
    }

    private void keepRunning() {
        WebView wv = webView();
        if (wv != null) { wv.onResume(); wv.resumeTimers(); }
    }

    @Override
    public void onPause() { super.onPause(); keepRunning(); }

    @Override
    public void onStop() { super.onStop(); keepRunning(); }
}
