using Avalonia;
using Avalonia.Controls;
using Avalonia.Media.Imaging;
using Avalonia.Platform;
using System.Reflection;

namespace BlockMind.Desktop.Controls;

public partial class Icon : UserControl
{
    public static readonly StyledProperty<string> IconNameProperty =
        AvaloniaProperty.Register<Icon, string>(nameof(IconName), defaultValue: "");

    public static readonly StyledProperty<int> IconSizeProperty =
        AvaloniaProperty.Register<Icon, int>(nameof(IconSize), defaultValue: 16);

    public string IconName
    {
        get => GetValue(IconNameProperty);
        set => SetValue(IconNameProperty, value);
    }

    public int IconSize
    {
        get => GetValue(IconSizeProperty);
        set => SetValue(IconSizeProperty, value);
    }

    private Avalonia.Controls.Image? _image;

    public Icon()
    {
        InitializeComponent();
        _image = this.FindControl<Avalonia.Controls.Image>("IconImage");
        PropertyChanged += OnPropertyChanged;
    }

    private void OnPropertyChanged(object? sender, AvaloniaPropertyChangedEventArgs e)
    {
        if (e.Property == IconNameProperty || e.Property == IconSizeProperty)
        {
            UpdateIcon();
        }
    }

    private void UpdateIcon()
    {
        if (_image == null || string.IsNullOrEmpty(IconName)) return;

        try
        {
            var assembly = Assembly.GetExecutingAssembly();
            var resourceName = $"BlockMind.Desktop.Assets.icons.{IconName}.svg";
            using var stream = assembly.GetManifestResourceStream(resourceName);
            if (stream != null)
            {
                var bitmap = new Bitmap(stream);
                _image.Source = bitmap;
                _image.Width = IconSize;
                _image.Height = IconSize;
            }
        }
        catch
        {
            // Icon not found — show nothing
        }
    }
}
