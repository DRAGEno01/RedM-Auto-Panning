import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.util.Random;
import java.awt.Robot;
import java.net.URI;
import java.awt.Desktop;
import javax.swing.Timer;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.InputStream;
import java.net.URL;
import java.util.Arrays;
import java.net.HttpURLConnection;
import java.io.BufferedInputStream;
import java.io.FileOutputStream;
import java.io.File;
import java.io.IOException;
import java.io.FileWriter;
import java.awt.AlphaComposite;
import java.awt.GradientPaint;
import java.awt.Graphics2D;
import java.awt.RenderingHints;
import javax.swing.border.Border;
import javax.swing.border.EmptyBorder;
import java.awt.geom.RoundRectangle2D;
import javax.swing.BorderFactory;

public class RedMPanning extends JFrame {
    private static final String VERSION = "1.102";
    private static final String VERSION_URL = "https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/version.txt";
    private JButton startButton;
    private JButton stopButton;
    private JLabel statusLabel;
    private boolean running;
    private Robot robot;
    private Random random;
    private Thread scriptThread;
    private Timer integrityMonitor;
    private final String repoUrl = "https://github.com/DRAGEno01/RedM-Auto-Panning/releases";
    private float mainOpacity = 0.0f;
    private Timer fadeInTimer;
    private JPanel mainPanel;
    private JLabel titleLabel;
    private JPanel buttonPanel;
    private JButton githubButton;
    private Timer connectionRetryTimer;
    private boolean hasCheckedVersion = false;

    public RedMPanning() {
        setTitle("DRAGEno01's RedM Auto Panning");
        setSize(700, 550);  // Increased size for better spacing
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setResizable(false);
        
        // Create main panel with a more sophisticated gradient
        mainPanel = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                Graphics2D g2d = (Graphics2D) g;
                g2d.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
                int w = getWidth(), h = getHeight();
                // Modern dark gradient with subtle blue tint
                GradientPaint gp = new GradientPaint(0, 0, new Color(28, 32, 38), 0, h, new Color(41, 46, 56));
                g2d.setPaint(gp);
                g2d.fillRect(0, 0, w, h);
                
                // Add subtle pattern overlay
                g2d.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC_OVER, 0.03f));
                for (int i = 0; i < h; i += 3) {
                    g2d.drawLine(0, i, w, i);
                }
                
                g2d.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC_OVER, mainOpacity));
            }
        };
        mainPanel.setLayout(new BorderLayout(30, 30));
        mainPanel.setBorder(BorderFactory.createEmptyBorder(35, 45, 35, 45));
        
        // Enhanced header panel with glass effect
        JPanel headerPanel = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                Graphics2D g2d = (Graphics2D) g;
                g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                g2d.setColor(new Color(255, 255, 255, 10));
                g2d.fillRoundRect(0, 0, getWidth(), getHeight(), 20, 20);
            }
        };
        headerPanel.setLayout(new BorderLayout(20, 0));
        headerPanel.setOpaque(false);
        headerPanel.setBorder(BorderFactory.createEmptyBorder(15, 20, 15, 20));
        
        // Version label with pill-shaped background
        JLabel versionLabel = new JLabel("v" + VERSION) {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2d = (Graphics2D) g;
                g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                g2d.setColor(new Color(255, 255, 255, 20));
                g2d.fillRoundRect(0, 0, getWidth(), getHeight(), 15, 15);
                super.paintComponent(g);
            }
        };
        versionLabel.setFont(new Font("Segoe UI", Font.BOLD, 14));
        versionLabel.setForeground(new Color(138, 147, 155));
        versionLabel.setBorder(BorderFactory.createEmptyBorder(5, 10, 5, 10));
        headerPanel.add(versionLabel, BorderLayout.EAST);
        
        // Enhanced title panel
        JPanel titlePanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 15, 0));
        titlePanel.setOpaque(false);
        
        // Animated icon
        JLabel iconLabel = new JLabel("🎮") {
            private float angle = 0;
            {
                Timer timer = new Timer(50, e -> {
                    angle += 0.05f;
                    setLocation(getX(), getY() + (int)(Math.sin(angle) * 0.7));
                    repaint();
                });
                timer.start();
            }
        };
        iconLabel.setFont(new Font("Segoe UI", Font.PLAIN, 36));
        titlePanel.add(iconLabel);
        
        titleLabel = new JLabel("RedM Auto Panning");
        titleLabel.setFont(new Font("Segoe UI", Font.BOLD, 32));
        titleLabel.setForeground(new Color(240, 240, 240));
        titlePanel.add(titleLabel);
        
        headerPanel.add(titlePanel, BorderLayout.WEST);
        mainPanel.add(headerPanel, BorderLayout.NORTH);
        
        // Enhanced status panel with glowing effect
        JPanel statusPanel = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2d = (Graphics2D) g;
                g2d.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                
                // Create glowing background
                Color glowColor = new Color(0, 255, 0, 10);
                for (int i = 0; i < 5; i++) {
                    g2d.setColor(new Color(glowColor.getRed(), glowColor.getGreen(), 
                        glowColor.getBlue(), glowColor.getAlpha() / (i + 1)));
                    g2d.fillRoundRect(i, i, getWidth() - (i * 2), getHeight() - (i * 2), 20, 20);
                }
                
                // Main background
                g2d.setColor(new Color(0, 0, 0, 80));
                g2d.fillRoundRect(0, 0, getWidth(), getHeight(), 20, 20);
            }
        };
        statusPanel.setLayout(new BorderLayout());
        statusPanel.setOpaque(false);
        statusPanel.setBorder(BorderFactory.createEmptyBorder(20, 25, 20, 25));
        
        statusLabel = new JLabel("Status: Idle");
        statusLabel.setFont(new Font("Segoe UI", Font.BOLD, 18));
        statusLabel.setForeground(new Color(141, 241, 138));
        statusPanel.add(statusLabel, BorderLayout.CENTER);
        
        // Center panel with enhanced layout
        JPanel centerPanel = new JPanel();
        centerPanel.setLayout(new BoxLayout(centerPanel, BoxLayout.Y_AXIS));
        centerPanel.setOpaque(false);
        centerPanel.setBorder(BorderFactory.createEmptyBorder(25, 0, 25, 0));
        centerPanel.add(statusPanel);
        centerPanel.add(Box.createVerticalStrut(35));
        
        // Enhanced button panel
        buttonPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 35, 0));
        buttonPanel.setOpaque(false);
        
        startButton = createStyledButton("START", new Color(40, 167, 69));
        stopButton = createStyledButton("STOP", new Color(220, 53, 69));
        stopButton.setEnabled(false);
        
        Dimension buttonSize = new Dimension(170, 55);
        startButton.setPreferredSize(buttonSize);
        stopButton.setPreferredSize(buttonSize);
        
        buttonPanel.add(startButton);
        buttonPanel.add(stopButton);
        
        centerPanel.add(buttonPanel);
        mainPanel.add(centerPanel, BorderLayout.CENTER);
        
        // Enhanced footer with GitHub button
        JPanel footerPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 0, 15));
        footerPanel.setOpaque(false);
        
        githubButton = createStyledButton("View on GitHub", new Color(51, 51, 51));
        githubButton.setPreferredSize(new Dimension(220, 45));
        githubButton.setFont(new Font("Segoe UI", Font.BOLD, 15));
        footerPanel.add(githubButton);
        
        mainPanel.add(footerPanel, BorderLayout.SOUTH);
        
        add(mainPanel);
        
        // Initialize components
        try {
            robot = new Robot();
            random = new Random();
        } catch (AWTException e) {
            e.printStackTrace();
        }
        
        // Add button listeners
        startButton.addActionListener(e -> startScript());
        stopButton.addActionListener(e -> stopScript());
        
        // Initialize system monitor
        integrityMonitor = new Timer(500, e -> {
            if (!validateIntegrity()) {
                handleValidationFailure();
            }
        });
        
        // Start fade-in animation after a delay
        fadeInTimer = new Timer(30, e -> {
            mainOpacity += 0.08f;
            if (mainOpacity >= 1.0f) {
                mainOpacity = 1.0f;
                fadeInTimer.stop();
                integrityMonitor.start();
            }
            titleLabel.setForeground(new Color(255, 255, 255, (int)(mainOpacity * 255)));
            statusLabel.setForeground(new Color(255, 255, 255, (int)(mainOpacity * 255)));
            buttonPanel.setVisible(mainOpacity > 0.5f);
            githubButton.setVisible(mainOpacity > 0.7f);
            mainPanel.repaint();
        });
        
        // Delay the start of fade-in
        Timer startDelay = new Timer(200, e -> {
            fadeInTimer.start();
            ((Timer)e.getSource()).stop();
        });
        startDelay.setRepeats(false);
        startDelay.start();
        
        // Initialize components with 0 opacity
        titleLabel.setForeground(new Color(255, 255, 255, 0));
        statusLabel.setForeground(new Color(255, 255, 255, 0));
        buttonPanel.setVisible(false);
        githubButton.setVisible(false);
        
        // Add version check on startup
        checkVersion();
    }
    
    private void startScript() {
        if (!running) {
            running = true;
            startButton.setEnabled(false);
            stopButton.setEnabled(true);
            
            scriptThread = new Thread(this::runScript);
            scriptThread.start();
        } else {
            JOptionPane.showMessageDialog(this, "Script is already running.");
        }
    }
    
    private void stopScript() {
        if (running) {
            running = false;
            startButton.setEnabled(true);
            stopButton.setEnabled(false);
            statusLabel.setText("Status: Stopped");
        }
    }

    private void runScript() {
        while (running) {
            double waitTime = 17.0 + random.nextDouble() * 3.0;
            waitTime = Math.max(17.0, waitTime); // Ensure minimum of 17 seconds
            updateStatusWithCountdown(waitTime);
            holdEnterRandomized();
        }
    }
    
    private void updateStatusWithCountdown(double totalSeconds) {
        long startTime = System.currentTimeMillis();
        while (running && System.currentTimeMillis() - startTime < totalSeconds * 1000) {
            double remainingSeconds = totalSeconds - (System.currentTimeMillis() - startTime) / 1000.0;
            if (remainingSeconds > 0) {
                SwingUtilities.invokeLater(() -> 
                    statusLabel.setText(String.format("Waiting: %.1f seconds", remainingSeconds))
                );
            }
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    private void holdEnterRandomized() {
        // Show "Performing Action" status
        SwingUtilities.invokeLater(() -> 
            statusLabel.setText("Performing Action")
        );

        // Calculate hold time with higher precision
        double holdTime = 0.9 + random.nextDouble() * 0.2;
        holdTime += (random.nextDouble() - 0.5) * 0.05;
        holdTime = Math.round(holdTime * 100000) / 100000.0;
        
        // Calculate wait time between 17 and 20 seconds
        double waitTime = 17.0 + random.nextDouble() * 3.0;
        waitTime = Math.max(17.0, Math.round(waitTime * 100000) / 100000.0); // Ensure minimum of 17 seconds
        
        // Introduce occasional "normal" behavior
        if (random.nextDouble() < 0.05) {
            holdTime = 1.0;
            waitTime = 17.0;
        }
        
        // Convert to milliseconds for Robot
        robot.keyPress(KeyEvent.VK_ENTER);
        try {
            Thread.sleep((long)(holdTime * 1000));
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        robot.keyRelease(KeyEvent.VK_ENTER);
    }

    private JButton createStyledButton(String text, Color color) {
        JButton button = new JButton(text) {
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2 = (Graphics2D) g.create();
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                
                // Create gradient effect
                GradientPaint gradient;
                if (getModel().isPressed()) {
                    gradient = new GradientPaint(0, 0, color.darker(), 0, getHeight(), color.darker().darker());
                } else if (getModel().isRollover()) {
                    gradient = new GradientPaint(0, 0, color.brighter(), 0, getHeight(), color);
                } else {
                    gradient = new GradientPaint(0, 0, color, 0, getHeight(), color.darker());
                }
                
                g2.setPaint(gradient);
                g2.fillRoundRect(0, 0, getWidth(), getHeight(), 15, 15);
                
                // Add subtle border
                g2.setColor(new Color(255, 255, 255, 50));
                g2.drawRoundRect(0, 0, getWidth() - 1, getHeight() - 1, 15, 15);
                
                g2.dispose();
                super.paintComponent(g);
            }
        };
        
        button.setForeground(Color.WHITE);
        button.setFont(new Font("Segoe UI", Font.BOLD, 16));
        button.setFocusPainted(false);
        button.setBorderPainted(false);
        button.setContentAreaFilled(false);
        
        // Add hover effect
        button.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseEntered(MouseEvent e) {
                button.setCursor(new Cursor(Cursor.HAND_CURSOR));
            }
        });
        
        return button;
    }
    
    private boolean validateIntegrity() {
        return true;  // Always return true since we're removing validation
    }
    
    private void handleValidationFailure() {
        // Empty method since we're removing validation
    }
    
    private void checkVersion() {
        // Initialize retry timer if not already created
        if (connectionRetryTimer == null) {
            connectionRetryTimer = new Timer(30000, e -> { // Check every 30 seconds
                if (!hasCheckedVersion) {
                    performVersionCheck();
                }
            });
            connectionRetryTimer.start();
        }
        
        performVersionCheck();
    }
    
    private void performVersionCheck() {
        new Thread(() -> {
            try {
                URL url = new URI(VERSION_URL).toURL();
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                connection.setConnectTimeout(5000);
                
                try (BufferedReader reader = new BufferedReader(new InputStreamReader(connection.getInputStream()))) {
                    StringBuilder content = new StringBuilder();
                    String line;
                    while ((line = reader.readLine()) != null) {
                        content.append(line.trim());
                    }
                    String latestVersion = content.toString().trim();
                    
                    hasCheckedVersion = true;
                    connectionRetryTimer.stop();
                    
                    // Debug prints
                    System.out.println("Raw content from version.txt: '" + content + "'");
                    System.out.println("Current version (LENGTH=" + VERSION.length() + "): '" + VERSION + "'");
                    System.out.println("Latest version (LENGTH=" + latestVersion.length() + "): '" + latestVersion + "'");
                    System.out.println("Versions are equal? " + VERSION.equals(latestVersion));
                    
                    // Convert versions to byte arrays to see if there are any hidden characters
                    System.out.println("Current version bytes: " + Arrays.toString(VERSION.getBytes()));
                    System.out.println("Latest version bytes: " + Arrays.toString(latestVersion.getBytes()));
                    
                    if (!VERSION.equals(latestVersion)) {
                        SwingUtilities.invokeLater(() -> showUpdateDialog(latestVersion));
                    }
                }
            } catch (Exception e) {
                e.printStackTrace();
                if (!hasCheckedVersion) {
                    SwingUtilities.invokeLater(() -> {
                        String message = String.format(
                            "<html><body style='width: 450px; padding: 20px; background-color: #1c2026; color: #e0e0e0;'>" +
                            "<div style='font-family: Segoe UI, Arial; text-align: center;'>" +
                            "<div style='background-color: #2d333b; padding: 25px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #383e47;'>" +
                            "<h2 style='margin: 0; font-size: 24px; color: #e2e2e2;'>Connection Warning</h2>" +
                            "</div>" +
                            "<p style='color: #b0b0b0; font-size: 14px; margin: 15px 0;'>" +
                            "Unable to check for updates. Please verify your internet connection.</p>" +
                            "<div style='background: linear-gradient(to bottom, #2d333b, #252931); " +
                            "padding: 20px; margin: 15px 0; border-radius: 12px; border: 1px solid #383e47;'>" +
                            "<p style='margin: 5px 0; color: #b0b0b0;'>" +
                            "<span style='color: #8b949e;'>Current version:</span> " +
                            "<span style='font-weight: bold; color: #58a6ff; background-color: #1c2026; padding: 4px 8px; border-radius: 6px; border: 1px solid #30363d;'>" + 
                            VERSION + "</span></p>" +
                            "</div>" +
                            "<p style='color: #8b949e; font-size: 13px; font-style: italic; margin-top: 15px;'>" +
                            "You can continue using the application,<br>but updates may be available.</p>" +
                            "</div></body></html>"
                        );

                        UIManager.put("OptionPane.background", new Color(28, 32, 38));
                        UIManager.put("Panel.background", new Color(28, 32, 38));
                        UIManager.put("OptionPane.messageForeground", new Color(224, 224, 224));
                        
                        Object[] options = {"Continue", "Check GitHub"};
                        JOptionPane optionPane = new JOptionPane(
                            message,
                            JOptionPane.WARNING_MESSAGE,
                            JOptionPane.YES_NO_OPTION,
                            null,
                            options,
                            options[0]
                        );
                        
                        JDialog dialog = optionPane.createDialog(null, "Connection Warning");
                        dialog.setBackground(new Color(28, 32, 38));
                        
                        // Style the buttons
                        Arrays.stream(dialog.getContentPane().getComponents())
                            .filter(c -> c instanceof JPanel)
                            .map(c -> (JPanel)c)
                            .flatMap(p -> Arrays.stream(p.getComponents()))
                            .filter(c -> c instanceof JButton)
                            .map(c -> (JButton)c)
                            .forEach(b -> {
                                b.setFont(new Font("Segoe UI", Font.BOLD, 12));
                                b.setBorderPainted(false);
                                b.setFocusPainted(false);
                                b.setContentAreaFilled(false);
                                b.setOpaque(true);
                                b.setBorder(BorderFactory.createEmptyBorder(8, 15, 8, 15));
                                b.setForeground(Color.WHITE);
                                b.setCursor(new Cursor(Cursor.HAND_CURSOR));
                                
                                if (b.getText().equals("Check GitHub")) {
                                    b.setBackground(new Color(88, 166, 255));
                                    b.addMouseListener(new MouseAdapter() {
                                        public void mouseEntered(MouseEvent e) {
                                            b.setBackground(new Color(77, 145, 223));
                                        }
                                        public void mouseExited(MouseEvent e) {
                                            b.setBackground(new Color(88, 166, 255));
                                        }
                                        public void mousePressed(MouseEvent e) {
                                            b.setBackground(new Color(66, 125, 192));
                                        }
                                    });
                                } else {
                                    b.setBackground(new Color(45, 51, 59));
                                    b.addMouseListener(new MouseAdapter() {
                                        public void mouseEntered(MouseEvent e) {
                                            b.setBackground(new Color(52, 59, 68));
                                        }
                                        public void mouseExited(MouseEvent e) {
                                            b.setBackground(new Color(45, 51, 59));
                                        }
                                        public void mousePressed(MouseEvent e) {
                                            b.setBackground(new Color(38, 43, 50));
                                        }
                                    });
                                }
                                
                                b.setBorder(BorderFactory.createCompoundBorder(
                                    BorderFactory.createLineBorder(new Color(0, 0, 0, 30), 1),
                                    BorderFactory.createEmptyBorder(8, 15, 8, 15)
                                ));
                            });
                        
                        dialog.setVisible(true);
                        Object selectedValue = optionPane.getValue();
                        
                        if (selectedValue != null && selectedValue.equals("Check GitHub")) {
                            try {
                                Desktop.getDesktop().browse(new URI("https://github.com/DRAGEno01/RedM-Auto-Panning/releases"));
                            } catch (Exception ex) {
                                ex.printStackTrace();
                            }
                        }
                    });
                }
                System.out.println("Version check failed: " + e.getMessage());
            }
        }).start();
    }
    
    private void showUpdateDialog(String latestVersion) {
        // Set dark theme for JOptionPane
        UIManager.put("OptionPane.background", new Color(28, 32, 38));
        UIManager.put("Panel.background", new Color(28, 32, 38));
        UIManager.put("OptionPane.messageForeground", new Color(224, 224, 224));
        
        JButton downloadButton = new JButton("Download") {
            {
                setFont(new Font("Segoe UI", Font.BOLD, 14));
                setForeground(Color.WHITE);
                setBackground(new Color(40, 167, 69));
                setBorderPainted(false);
                setFocusPainted(false);
                setCursor(new Cursor(Cursor.HAND_CURSOR));
                setPreferredSize(new Dimension(150, 40));
                
                addMouseListener(new MouseAdapter() {
                    public void mouseEntered(MouseEvent e) {
                        setBackground(new Color(46, 189, 79));
                    }
                    public void mouseExited(MouseEvent e) {
                        setBackground(new Color(40, 167, 69));
                    }
                    public void mousePressed(MouseEvent e) {
                        setBackground(new Color(35, 146, 60));
                    }
                });
            }
            
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2 = (Graphics2D) g.create();
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                GradientPaint gradient = new GradientPaint(0, 0, getBackground(), 0, getHeight(), getBackground().darker());
                g2.setPaint(gradient);
                g2.fillRoundRect(0, 0, getWidth(), getHeight(), 15, 15);
                g2.dispose();
                super.paintComponent(g);
            }
        };
        
        JButton exitButton = new JButton("Exit") {
            {
                setFont(new Font("Segoe UI", Font.BOLD, 14));
                setForeground(Color.WHITE);
                setBackground(new Color(220, 53, 69));
                setBorderPainted(false);
                setFocusPainted(false);
                setCursor(new Cursor(Cursor.HAND_CURSOR));
                setPreferredSize(new Dimension(150, 40));
                
                addMouseListener(new MouseAdapter() {
                    public void mouseEntered(MouseEvent e) {
                        setBackground(new Color(239, 58, 75));
                    }
                    public void mouseExited(MouseEvent e) {
                        setBackground(new Color(220, 53, 69));
                    }
                    public void mousePressed(MouseEvent e) {
                        setBackground(new Color(192, 46, 60));
                    }
                });
            }
            
            @Override
            protected void paintComponent(Graphics g) {
                Graphics2D g2 = (Graphics2D) g.create();
                g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
                GradientPaint gradient = new GradientPaint(0, 0, getBackground(), 0, getHeight(), getBackground().darker());
                g2.setPaint(gradient);
                g2.fillRoundRect(0, 0, getWidth(), getHeight(), 15, 15);
                g2.dispose();
                super.paintComponent(g);
            }
        };
        
        // Create progress bar (initially invisible)
        JProgressBar progressBar = new JProgressBar(0, 100);
        progressBar.setPreferredSize(new Dimension(400, 30));
        progressBar.setMaximumSize(new Dimension(400, 30));
        progressBar.setAlignmentX(Component.CENTER_ALIGNMENT);
        progressBar.setBackground(new Color(45, 51, 59));
        progressBar.setForeground(new Color(40, 167, 69));
        progressBar.setBorderPainted(false);
        progressBar.setStringPainted(true);
        progressBar.setFont(new Font("Segoe UI", Font.BOLD, 14));
        progressBar.setVisible(false);
        
        // Progress status label (initially invisible)
        JLabel progressStatus = new JLabel("Preparing download...");
        progressStatus.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        progressStatus.setForeground(new Color(176, 176, 176));
        progressStatus.setAlignmentX(Component.CENTER_ALIGNMENT);
        progressStatus.setVisible(false);
        
        // Add progress components to content panel
        JPanel contentPanel = new JPanel();
        contentPanel.setLayout(new BoxLayout(contentPanel, BoxLayout.Y_AXIS));
        contentPanel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));
        contentPanel.add(Box.createVerticalStrut(20));
        contentPanel.add(progressStatus);
        contentPanel.add(Box.createVerticalStrut(10));
        contentPanel.add(progressBar);
        
        // Add action listeners
        downloadButton.addActionListener(e -> {
            // Hide buttons
            buttonPanel.removeAll();
            buttonPanel.revalidate();
            buttonPanel.repaint();
            
            // Show progress components
            progressBar.setVisible(true);
            progressStatus.setVisible(true);
            
            // Start download in background
            new Thread(() -> {
                try {
                    long startTime = System.currentTimeMillis();
                    String newFilePath = "RedMPanning.java";
                    URL url = new URL(String.format("https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/code/V%s/RedMPanning.java", latestVersion));
                    HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                    int fileSize = connection.getContentLength();
                    
                    try (BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                         FileWriter out = new FileWriter(newFilePath)) {
                        
                        char[] buffer = new char[1024];
                        int charsRead;
                        long totalCharsRead = 0;
                        
                        while ((charsRead = in.read(buffer)) != -1) {
                            out.write(buffer, 0, charsRead);
                            totalCharsRead += charsRead;
                            
                            // Calculate progress
                            final int realProgress = (int) ((totalCharsRead * 100) / fileSize);
                            
                            // Ensure minimum 5 seconds duration
                            long elapsedTime = System.currentTimeMillis() - startTime;
                            int adjustedProgress = Math.min(realProgress, (int)(elapsedTime / 50));
                            
                            final int displayProgress = adjustedProgress;
                            SwingUtilities.invokeLater(() -> {
                                progressBar.setValue(displayProgress);
                                if (displayProgress < 30) {
                                    progressStatus.setText("Downloading update files...");
                                } else if (displayProgress < 60) {
                                    progressStatus.setText("Verifying download...");
                                } else if (displayProgress < 90) {
                                    progressStatus.setText("Preparing to install...");
                                } else {
                                    progressStatus.setText("Finalizing update...");
                                }
                            });
                            
                            Thread.sleep(50);
                        }
                        
                        // Ensure minimum duration
                        while (System.currentTimeMillis() - startTime < 5000) {
                            Thread.sleep(50);
                            final long elapsedTime = System.currentTimeMillis() - startTime;
                            final int finalProgress = Math.min(100, (int)(elapsedTime / 50));
                            SwingUtilities.invokeLater(() -> {
                                progressBar.setValue(finalProgress);
                                if (finalProgress == 100) {
                                    progressStatus.setText("Update complete!");
                                }
                            });
                        }
                        
                        // Show completion message
                        SwingUtilities.invokeLater(() -> {
                            JOptionPane.showMessageDialog(
                                this,
                                "Update downloaded successfully!\nPlease recompile and restart the application.",
                                "Update Complete",
                                JOptionPane.INFORMATION_MESSAGE
                            );
                            System.exit(0);
                        });
                        
                    }
                } catch (Exception ex) {
                    ex.printStackTrace();
                    SwingUtilities.invokeLater(() -> {
                        JOptionPane.showMessageDialog(
                            this,
                            "Error downloading update: " + ex.getMessage(),
                            "Update Failed",
                            JOptionPane.ERROR_MESSAGE
                        );
                    });
                }
            }).start();
        });
        
        exitButton.addActionListener(e -> {
            System.exit(0);
        });
        
        Object[] options = {downloadButton, exitButton};

        String message = String.format(
            "<html><body style='width: 450px; padding: 20px; background-color: #1c2026; color: #e0e0e0;'>" +
            "<div style='font-family: Segoe UI, Arial; text-align: center;'>" +
            "<div style='background-color: #2d333b; padding: 25px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #383e47;'>" +
            "<h2 style='margin: 0; font-size: 24px; color: #ff6b6b;'>Update Required</h2>" +
            "</div>" +
            "<p style='color: #b0b0b0; font-size: 14px; margin: 15px 0;'>" +
            "Your version is outdated and no longer supported.</p>" +
            "<div style='background: linear-gradient(to bottom, #2d333b, #252931); " +
            "padding: 20px; margin: 15px 0; border-radius: 12px; border: 1px solid #383e47;'>" +
            "<p style='margin: 5px 0; color: #b0b0b0;'>" +
            "<span style='color: #8b949e;'>Current version:</span> " +
            "<span style='font-weight: bold; color: #ff6b6b; background-color: #1c2026; padding: 4px 8px; border-radius: 6px; border: 1px solid #30363d;'>" +
            VERSION + "</span></p>" +
            "<p style='margin: 5px 0; color: #b0b0b0;'>" +
            "<span style='color: #8b949e;'>Latest version:</span> " +
            "<span style='font-weight: bold; color: #3fb950; background-color: #1c2026; padding: 4px 8px; border-radius: 6px; border: 1px solid #30363d;'>" +
            latestVersion + "</span></p>" +
            "</div>" +
            "<p style='color: #8b949e; font-size: 13px; font-style: italic; margin-top: 15px;'>" +
            "Please download and install the latest version<br>to ensure optimal performance and security.</p>" +
            "</div></body></html>"
        );

        JOptionPane optionPane = new JOptionPane(
            message,
            JOptionPane.WARNING_MESSAGE,
            JOptionPane.YES_NO_OPTION,
            null,
            options,
            options[0]
        );
        
        JDialog dialog = optionPane.createDialog(this, "Update Required");
        dialog.setBackground(new Color(28, 32, 38));
        
        dialog.setVisible(true);
        Object selectedValue = optionPane.getValue();
        
        if (selectedValue != null && selectedValue.equals("Download")) {
            downloadUpdate(latestVersion);
        } else {
            System.exit(0);
        }
    }

    private void downloadUpdate(String latestVersion) {
        // Create progress panel
        JPanel progressPanel = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                Graphics2D g2d = (Graphics2D) g;
                g2d.setRenderingHint(RenderingHints.KEY_RENDERING, RenderingHints.VALUE_RENDER_QUALITY);
                int w = getWidth(), h = getHeight();
                GradientPaint gp = new GradientPaint(0, 0, new Color(28, 32, 38), 0, h, new Color(41, 46, 56));
                g2d.setPaint(gp);
                g2d.fillRect(0, 0, w, h);
            }
        };
        progressPanel.setLayout(new BoxLayout(progressPanel, BoxLayout.Y_AXIS));
        progressPanel.setBorder(BorderFactory.createEmptyBorder(50, 40, 50, 40));
        
        // Header
        JLabel headerLabel = new JLabel("Downloading Update");
        headerLabel.setFont(new Font("Segoe UI", Font.BOLD, 28));
        headerLabel.setForeground(Color.WHITE);
        headerLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        
        // Status label
        JLabel statusLabel = new JLabel("Preparing download...");
        statusLabel.setFont(new Font("Segoe UI", Font.PLAIN, 14));
        statusLabel.setForeground(new Color(176, 176, 176));
        statusLabel.setAlignmentX(Component.CENTER_ALIGNMENT);
        
        // Progress bar
        JProgressBar progressBar = new JProgressBar(0, 100);
        progressBar.setPreferredSize(new Dimension(400, 30));
        progressBar.setMaximumSize(new Dimension(400, 30));
        progressBar.setAlignmentX(Component.CENTER_ALIGNMENT);
        progressBar.setBackground(new Color(45, 51, 59));
        progressBar.setForeground(new Color(40, 167, 69));
        progressBar.setBorderPainted(false);
        progressBar.setStringPainted(true);
        progressBar.setFont(new Font("Segoe UI", Font.BOLD, 14));
        
        // Add components
        progressPanel.add(headerLabel);
        progressPanel.add(Box.createVerticalStrut(30));
        progressPanel.add(statusLabel);
        progressPanel.add(Box.createVerticalStrut(30));
        progressPanel.add(progressBar);
        
        // Add progress panel to content
        getContentPane().removeAll();
        getContentPane().add(progressPanel);
        revalidate();
        repaint();
        
        // Start download in background
        new Thread(() -> {
            try {
                long startTime = System.currentTimeMillis();
                String newFilePath = "RedMPanning.java";
                URL url = new URL(String.format("https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/code/V%s/RedMPanning.java", latestVersion));
                HttpURLConnection connection = (HttpURLConnection) url.openConnection();
                int fileSize = connection.getContentLength();
                
                try (BufferedReader in = new BufferedReader(new InputStreamReader(connection.getInputStream()));
                     FileWriter out = new FileWriter(newFilePath)) {
                    
                    char[] buffer = new char[1024];
                    int charsRead;
                    long totalCharsRead = 0;
                    
                    while ((charsRead = in.read(buffer)) != -1) {
                        out.write(buffer, 0, charsRead);
                        totalCharsRead += charsRead;
                        
                        // Calculate progress
                        final int realProgress = (int) ((totalCharsRead * 100) / fileSize);
                        
                        // Ensure minimum 5 seconds duration
                        long elapsedTime = System.currentTimeMillis() - startTime;
                        int adjustedProgress = Math.min(realProgress, (int)(elapsedTime / 50));
                        
                        final int displayProgress = adjustedProgress;
                        SwingUtilities.invokeLater(() -> {
                            progressBar.setValue(displayProgress);
                            if (displayProgress < 30) {
                                statusLabel.setText("Downloading update files...");
                            } else if (displayProgress < 60) {
                                statusLabel.setText("Verifying download...");
                            } else if (displayProgress < 90) {
                                statusLabel.setText("Preparing to install...");
                            } else {
                                statusLabel.setText("Finalizing update...");
                            }
                        });
                        
                        Thread.sleep(50);
                    }
                    
                    // Ensure minimum duration
                    while (System.currentTimeMillis() - startTime < 5000) {
                        Thread.sleep(50);
                        final long elapsedTime = System.currentTimeMillis() - startTime;
                        final int finalProgress = Math.min(100, (int)(elapsedTime / 50));
                        SwingUtilities.invokeLater(() -> {
                            progressBar.setValue(finalProgress);
                            if (finalProgress == 100) {
                                statusLabel.setText("Update complete!");
                            }
                        });
                    }
                    
                    // Show completion message
                    SwingUtilities.invokeLater(() -> {
                        JOptionPane.showMessageDialog(
                            this,
                            "Update downloaded successfully!\nPlease recompile and restart the application.",
                            "Update Complete",
                            JOptionPane.INFORMATION_MESSAGE
                        );
                        System.exit(0);
                    });
                    
                }
            } catch (Exception e) {
                e.printStackTrace();
                SwingUtilities.invokeLater(() -> {
                    JOptionPane.showMessageDialog(
                        this,
                        "Error downloading update: " + e.getMessage(),
                        "Update Failed",
                        JOptionPane.ERROR_MESSAGE
                    );
                });
            }
        }).start();
    }

    // Make sure to clean up the timer when the application closes
    @Override
    public void dispose() {
        if (connectionRetryTimer != null) {
            connectionRetryTimer.stop();
        }
        super.dispose();
    }
    
    public static void main(String[] args) {
        try {
            // Set system look and feel for better UI appearance
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        SwingUtilities.invokeLater(() -> {
            RedMPanning app = new RedMPanning();
            app.setLocationRelativeTo(null);
            app.setVisible(true);
        });
    }
}
